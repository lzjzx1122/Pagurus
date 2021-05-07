from container import Container
import docker
from port_manager import PortManager
import gevent
from gevent import monkey
monkey.patch_all()
from gevent.queue import Queue
import file_controller
import os
import time
import json
import couchdb
import subprocess
import shutil



class PrewarmManager:
    def __init__(self, prewarm_limit, port_manager, package_counter):
        self.prewarm_limit = prewarm_limit
        self.client = docker.from_env()
        self.port_manager = port_manager
        self.package_counter = package_counter
        self.prewarm_pools = []
        for _ in range(prewarm_limit):
            self.prewarm()
        self.function_path = '/root/sosp/Pagurus/interaction_controller/aws_actions/'
        self.virtualenv_path = '/root/sosp/Pagurus/intraaction_controller/virtualenv/'

    def prewarm(self):
        port = self.port_manager.get()
        container = Container.create(self.client, 'pagurus_prewarm_base', port, 'exec')
        self.prewarm_pools.append(container)

    def get_prewarmed_container(self, function_name):
        try:
            container = self.prewarm_pools.pop()
        except Exception:
            return None, 0
        source_path = self.function_path + function_name
        virtualenv_path = self.virtualenv_path + function_name + '/lib/python3.6/site-packages'
        container_dir = file_controller.get_container_dir(container.container.id)
        # send virtual environment to docker
        p_start = time.time()
        if not self.package_counter.no_package(function_name):
            if os.path.exists(virtualenv_path):
                os.system('docker cp ' + virtualenv_path + ' ' + container.container.id + ':/proxy/exec/site-packages/')
        p_end = time.time()
        # copy source code to container
        os.system('cp -rf ' + source_path + '/* ' + container_dir)
        # generate another base container
        job = gevent.spawn_later(0.1, self.prewarm) 
        # print('----Prewarmed container for ' + function_name + ', Container name: ' + container.container.name + '----')
        return container, p_end - p_start

class PackageCounter:
    def __init__(self):
        self.package_size_path = '/root/sosp/Pagurus/intraaction_controller/build_file/packages.json'
        self.build_limit = 4
        self.package_size = dict()
        self.counter = dict()
        self.q = Queue()
        self.no_package_functions = set()

        size_file = open(self.package_size_path, 'r', encoding='utf-8')
        self.dependencies = json.load(size_file)
        size_file.close()
        for function in self.dependencies:
            if len(self.dependencies[function]) == 0:
                self.no_package_functions.add(function)
            for package in self.dependencies[function]:
                self.counter[package] = 0
                self.package_size[package] = int(self.dependencies[function][package])
        gevent.spawn(self.visit_consumer)

    def no_package(self, function_name):
        return function_name in self.no_package_functions

    def visit(self, function_name):
        self.q.put(function_name)

    def visit_consumer(self):
        while True:
            function_name = self.q.get()
            #print('Executing function: ' + function_name)
            for package in self.dependencies[function_name]:
                self.counter[package] = self.counter[package] + 1
    
    def refresh(self):
        benefit_cost = dict()
        for package in self.counter:
            if self.counter[package] == 0:
                benefit_cost[package] = 1e9
            else:
                benefit_cost[package] = float(self.package_size[package]) / float(self.counter[package])
        sorted_packages = sorted(benefit_cost.items(), key = lambda kv: (kv[1], kv[0]))
        top_packages = list()
        for index in range(self.build_limit):
            top_packages.append(sorted_packages[index][0])
        for package in self.counter:
            self.counter[package] = 0
        return top_packages


class SockPrewarmManager:
    def __init__(self, prewarm_limit, port_manager, package_counter):
        self.rebuild_interval = 3600 / 2
        self.available = True
        self.prewarm_limit = prewarm_limit
        self.client = docker.from_env()
        self.port_manager = port_manager
        self.prewarm_pools = []
        self.function_path = '/root/sosp/Pagurus/interaction_controller/aws_actions/'
        self.virtualenv_path = '/root/sosp/Pagurus/intraaction_controller/virtualenv/'
        self.container_path = '/root/sosp/Pagurus/prewarm_container'
        self.package_counter = package_counter
        self.aliases = {'pillow': ['Pillow'], 'PyYAML': ['yaml', 'YAML'], 'scikit-video': ['skvideo']}
        db_server = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984/')
        if 'debug' in db_server: 
            db_server.delete('debug')
        self.db = db_server.create('debug')
        self.rebuild_image()
        self.top_packages = list()

    def rebuild_image(self):
        gevent.spawn_later(self.rebuild_interval, self.rebuild_image)
        self.available = False
        for container in self.prewarm_pools:
            container.container.stop()
            container.container.remove()
        self.prewarm_pools = []
        self.top_packages = self.package_counter.refresh()
        re_path = self.container_path + '/requirements.txt'
        os.system('sudo rm ' + re_path)
        re_file = open(re_path, 'w', encoding='utf-8') 
        for package in self.top_packages:
            re_file.write(package + '\n')
        re_file.close()
        process = subprocess.call(['docker', 'build', '--no-cache', '-t', 'pagurus_prewarm_base', self.container_path])
        # thread = gevent.spawn(os.system, 'docker build --no-cache -t pagurus_prewarm_base ' + self.container_path)
        # gevent.joinall([thread])
        for _ in range(self.prewarm_limit):
            self.prewarm()
        self.available = True

    def prewarm(self):
        container = Container.create(self.client, 'pagurus_prewarm_base', self.port_manager.get(), 'exec')
        self.prewarm_pools.append(container)

    def check_related(self, file_name):
        for package in self.top_packages:
            if package in file_name:
                return True
            if package in self.aliases:
                for alias in self.aliases:
                    if alias in file_name:
                        return True
            if package.replace('-', '_') in file_name:
                return True
        return False

    def get_prewarmed_container(self, function_name):
        self.db[str(time.time())] = {'name': function_name}
        #print('----Getting prewarmed container----')
        if not self.available:
            return None, 0
        try:
            container = self.prewarm_pools.pop()
        except Exception:
            return None, 0
        source_path = self.function_path + function_name
        virtualenv_path = self.virtualenv_path + function_name
        container_dir = file_controller.get_container_dir(container.container.id)
        # send virtual environment to docker
        p_start = time.time()
        devNull = open(os.devnull, 'w')
        if not self.package_counter.no_package(function_name):

            vp_path = 'lib/python3.6/site-packages'
            '''
            rsync_command = ['rsync', '-av']
            #rsync_command = 'rsync -av'
            for cur_path, cur_dirs, cur_files in os.walk(virtualenv_path + '/lib/python3.6/site-packages'):
                for file_name in cur_dirs:
                    if self.check_related(file_name):
                        #rsync_command += ' --exclude ' + file_name
                        rsync_command.append('--exclude')
                        rsync_command.append(file_name)
            #rsync_command += ' ' + virtualenv_path + '/lib/python3.6/site-packages/* ' + container_dir + '/site-packages'
            rsync_command.append(virtualenv_path + '/lib/python3.6/site-packages/')
            rsync_command.append(container_dir + '/site-packages')
            process = subprocess.Popen(rsync_command, stdout = devNull)
            process.wait()
            #os.system(rsync_command)
            '''
            source = virtualenv_path + '/lib/python3.6/site-packages'
            destination = container_dir + '/site-packages'
            ignore_prefix = list()
            for package in self.top_packages:
                ignore_prefix.append(package + '*')
            print(ignore_prefix)
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*tuple(ignore_prefix)))

        p_end = time.time()
        # copy source code to container
        #os.system('cp -rf ' + source_path + '/* ' + container_dir)
        # process = subprocess.Popen(['cp', source_path + '/main.py', container_dir], stdout = devNull)
        # process.wait()
        shutil.copy(source_path + '/main.py', container_dir)
        #generate another base container
        job = gevent.spawn_later(0.1, self.prewarm) 
        #print('----Prewarmed container for ' + function_name + ', Container name: ' + container.container.name + '----')
        return container, p_end - p_start

