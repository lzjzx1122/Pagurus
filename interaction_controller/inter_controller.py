import shutil

from gevent import monkey

monkey.patch_all()
import gevent
import subprocess
import os
import time
import docker
import queue
import couchdb
import random
import json
import psutil
import numpy as np
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import requests
import socket
import uuid


class inter_controller():
    def __init__(self, intra_url, package_path):
        self.intra_url = intra_url
        self.similar_actions = 30
        self.sharing_actions = 8
        self.repacked_renters = {}
        self.renter_lender_info = {}  # {'renter A': {'lender B': cos, 'lender C':cos}}
        self.lender_renter_info = {}  # {'lender A': {'renter B': cos, 'renter C':cos}}
        self.repack_info = {}  # {'lender A': {'renter B': cos, 'renter C':cos}}
        self.repack_packages = {}  # {'lender A': {'lib A':'ver A', 'lib B': 'ver B'}}
        self.all_packages = {}
        self.last_request = {}
        self.package_path = package_path
        self.load_packages()
        self.create_venv()  # create venv for each action with their name dir.
        self.update_repack_cycle = 60 * 30
        self.check_redirect_cycle = 60
        db_server = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984/')
        if 'renter_lender_info' in db_server:
            db_server.delete('renter_lender_info')
        self.db = db_server.create('renter_lender_info')
        if 'repack_info' in db_server:
            db_server.delete('repack_info')
        self.db_repack = db_server.create('repack_info')
        self.cold_start = {}
        self.has_lender = {}
        self.repack_period = 60 * 60 / 2

    def create_venv(self):
        virtualenv_path = './virtualenv/'
        init_file = open('init_venv.bash', 'w', encoding='utf-8')
        for action in self.all_packages:
            init_file.write('virtualenv -p /usr/bin/python3 ' + virtualenv_path + action + '\n')
            init_file.write('source ' + virtualenv_path + action + '/bin/activate\n')
            for package, version in self.all_packages[action].items():
                init_file.write('pip3 install ' + package + '==' + version + '\n')
            init_file.write('deactivate\n')
        init_file.close()
        ret = subprocess.call('/home/openwhisk/sosp/Pagurus/interaction_controller/init_venv.bash', shell=True, executable='/bin/bash')
        print('init_venv : return_value :', ret)

    def print_info(self):
        print('lender_renter_info:', self.lender_renter_info)
        '''
        for lender in self.lender_renter_info:
            print(lender, end = ': ')
            for (renter, value) in self.lender_renter_info[lender].items():
                print(renter, ' ', value, end = ' ')
            print('')
        '''
        print('renter_lender_info:', self.renter_lender_info)
        '''
        for renter in self.renter_lender_info:
            print(renter, end = ': ')
            for (lender, value) in self.renter_lender_info[renter].items():
                print(lender, ' ', value, end = ' ')
            print('')
        '''

    def load_packages(self):
        all_packages = open(self.package_path, encoding='utf-8')
        all_packages_content = all_packages.read()
        self.all_packages = json.loads(all_packages_content)
        for action in self.all_packages.keys():
            self.last_request[action] = 0

    def remove_lender(self, lender):
        if lender in self.lender_renter_info:
            for renter in list(self.lender_renter_info[lender].keys()):
                self.renter_lender_info[renter].pop(lender)
            self.lender_renter_info.pop(lender)

    def add_lender(self, lender):
        renters = self.repack_info[lender].copy()
        self.lender_renter_info[lender] = renters
        for (k, v) in renters.items():
            if k not in self.renter_lender_info.keys():
                self.renter_lender_info.update({k: {lender: v}})
            else:
                self.renter_lender_info[k].update({lender: v})

    def choose_renters(self, lender):
        all_packages = self.all_packages.copy()
        tmp = list(all_packages.items())
        random.shuffle(tmp)
        all_packages = dict(tmp)
        packages = all_packages.pop(lender)
        sim = dict()
        P = dict()
        for (p, v) in packages.items():
            P[p] = v
        for (candidate, p_dict) in all_packages.items():
            not_conflict = True
            for (p, v) in P.items():
                if (p in p_dict) and p_dict[p] != v:
                    not_conflict = False
                    break
            if not_conflict:
                sim[candidate] = None
                for (p, v) in p_dict.items():
                    if p not in P:
                        P[p] = v

        lender_vector = []
        for p in P.keys():
            if p in packages.keys():
                lender_vector.append(1)
            else:
                lender_vector.append(0)

        for candidate in sim.keys():
            candidate_vector = []
            for p in P.keys():
                if p in all_packages[candidate].keys():
                    candidate_vector.append(1)
                else:
                    candidate_vector.append(0)
            tmp = np.linalg.norm(lender_vector) * np.linalg.norm(candidate_vector)
            if tmp == 0:
                sim[candidate] = 1
            else:
                sim[candidate] = np.dot(lender_vector, candidate_vector) / tmp

        renters = dict()
        requirements = dict()
        similar_actions = self.similar_actions
        while len(sim) > 0 and similar_actions > 0:
            renter = max(sim, key=sim.get)
            for (p, v) in all_packages[renter].items():
                requirements.update({p: v})
            renters.update({renter: sim[renter]})
            similar_actions -= 1
            sim.pop(renter)

        # Note that the similar_actions parameter may be too large that few packages coexist, and the greedy method need to be modifed.
        # renters does not include lender? -> lender is only a flag?
        # In generate_repacked_image(), package version is unspecified?

        safe_requirements = dict()
        for package in requirements:
            coexist = True
            for renter in renters:
                if package not in all_packages[renter]:
                    coexist = False
                    break
            if coexist:
                safe_requirements[package] = requirements.get(package)
        requirements = safe_requirements

        return renters, requirements

    def generate_base_image(self, action_name):
        requirements = self.all_packages[action_name]
        save_path = 'images_save/' + action_name + '/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        requirement_str = ''
        for requirement in requirements:
            requirement_str += ' ' + requirement

        with open(save_path + 'Dockerfile', 'w') as f:
            f.write('FROM pagurus_base\n')
            # f.write('COPY pip.conf /etc/pip.conf\n')
            # f.write('COPY {}.zip /proxy/actions/action_{}.zip\n'.format(action_name, action_name))
            if requirement_str != '':
                f.write('RUN pip3 --no-cache-dir install{}'.format(requirement_str))

        # os.system('cd {} && cp ../../actions/pip.conf .'.format(save_path))
        # os.system('cd {} && cp ../../actions/{}.zip . && docker build --no-cache -t action_{} .'.format(save_path, action_name, action_name))
        os.system('cd {} && docker build --no-cache -t action_{} .'.format(save_path, action_name, action_name))

    def generate_repacked_image(self, action_name, renters, requirements, repack_updating=False):
        save_path = 'images_save/' + action_name + '_repack/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        self.remove_lender(action_name)

        # prepare for dockerfile context

        shutil.rmtree(save_path + 'private_packages', ignore_errors=True)
        ignore_prefix = list()
        for package in requirements:
            ignore_prefix.append(package + '*')
        virtualenv_path = './virtualenv/'
        for renter in renters:
            # use symlink?
            shutil.copytree(virtualenv_path + renter + '/lib/python3.7/site-packages',
                            save_path + 'private_packages/' + renter,
                            True, ignore=shutil.ignore_patterns(*tuple(ignore_prefix)))

        requirement_str = ''
        for requirement in requirements:
            requirement_str += ' ' + requirement

        with open(save_path + 'Dockerfile', 'w') as f:
            f.write('FROM action_{}\n'.format(action_name))
            # f.write('COPY pip.conf /etc/pip.conf\n')
            # for renter in renters.keys():
            #    f.write('COPY {}.zip /proxy/actions/action_{}.zip\n'.format(renter, renter))
            if requirement_str != '':
                # install virtualenv also for latter opt
                f.write('RUN pip3 --no-cache-dir install {}\n'.format(requirement_str))

            useradd_command = ''
            for renter in renters:
                if useradd_command == '':
                    useradd_command = 'useradd -ms /bin/bash ' + renter
                else:
                    useradd_command += ' && useradd -ms /bin/bash ' + renter
            if useradd_command != '':
                f.write('RUN ' + useradd_command + '\n')

            # copy private package for each renter into their home dir.
            f.write('COPY private_packages /home\n')

        # os.system('cd {} && cp ../../actions/pip.conf .'.format(save_path))
        # os.system('cd {} && cp ../../actions/pip.conf .'.format(save_path))
        # for renter in renters.keys():
        #    os.system('cd {} && cp ../../actions/{}.zip .'.format(save_path, renter))
        os.system('cd {} && docker build --no-cache -t action_{}_repack .'.format(save_path, action_name))

        if repack_updating == True:
            self.remove_lender(action_name)
            while True:
                try:
                    url = self.intra_url + action_name + '/repack'
                    res = requests.post(url)
                    if res.text == 'OK':
                        break
                except Exception:
                    time.sleep(0.01)

    def requirements_changed(self, action_name, requirements):
        if len(requirements) == len(self.repack_packages[action_name]):
            for (p, v) in self.repack_packages[action_name].items():
                if (p not in requirements.keys()) or requirements[p] != v:
                    return True
            return False
        else:
            return True

    def repack(self, action_name, repack_updating=False):
        renters, requirements = self.choose_renters(action_name)
        self.repacked_renters[action_name] = renters
        # print('get_renters: ', renters, requirements)
        # if action_name not in self.repack_packages.keys() or self.requirements_changed(action_name, requirements):
        self.generate_repacked_image(action_name, renters, requirements, repack_updating)
        self.repack_packages[action_name] = requirements
        return renters

    def periodical_repack(self):
        value = {}
        for action in self.all_packages:
            value[action] = 1
        cold_start = self.cold_start.copy()
        # cold_start = {'video': 100, 'linpack': 20}
        self.cold_start = {}
        for action in cold_start:
            value[action] = cold_start[action]
        position = []
        for action in value:
            for i in range(value[action]):
                position.append(action)

        randrange = len(position) - 1
        repack_info = {}
        for lender in self.all_packages:
            renters = {}
            for i in range(self.sharing_actions):
                renter = position[random.randint(0, randrange)]
                while renter in renters or renter not in self.repacked_renters[lender]:
                    renter = position[random.randint(0, randrange)]
                renters[renter] = 1
            repack_info[lender] = renters

        '''
        for lender in self.all_packages:
            self.has_lender[lender] = True
        '''

        self.repack_info = repack_info
        self.renter_lender_info = {}
        self.lender_renter_info = {}
        for lender in self.has_lender:
            if self.has_lender[lender] == True:
                renters = repack_info[lender].copy()
                self.lender_renter_info[lender] = renters
                for (k, v) in renters.items():
                    if k not in self.renter_lender_info.keys():
                        self.renter_lender_info.update({k: {lender: v}})
                    else:
                        self.renter_lender_info[k].update({lender: v})
        self.db_repack[str(time.time())] = {'repack_info': self.repack_info,
                                            'lender_renter_info': self.lender_renter_info,
                                            'renter_lender_info': self.renter_lender_info}
        # print('lender_renter:', self.lender_renter_info)
        # print('renter_lender:', self.renter_lender_info)

    def schedule_lender(self, action_name):
        if action_name in self.renter_lender_info.keys() and len(self.renter_lender_info[action_name]) > 0:
            # lender = max(self.renter_lender_info[action_name], key = self.renter_lender_info[action_name].get) 
            lender_list = list(self.renter_lender_info[action_name].keys())
            lender = lender_list[random.randint(0, len(lender_list) - 1)]
            try:
                res = requests.get(self.intra_url + lender + '/lend')
                if res.text == 'no lender':
                    return None
                else:
                    self.db[uuid.uuid4().hex] = {'renter': action_name, 'lender': lender, 'time': time.time()}
                    res_dict = json.loads(res.text)
                    return lender, res_dict['id'], res_dict['port']
            except Exception as e:
                print('e:', e)
                return None
        else:
            return None

    def get_lender_list(self):
        lender_containers = {}
        containers = {}
        for action in self.all_packages.keys():
            res = requests.get(self.intra_url + action + '/status')
            status = json.loads(res.text)
            lender_containers[action] = status['lender']
            containers[action] = status['exec'][0]
        for renter in self.all_packages.keys():
            if renter in self.renter_lender_info:
                for lender in self.renter_lender_info[renter]:
                    containers[renter] += lender_containers[lender]
        return containers

    def check_redirect(self):
        for action in self.all_packages.keys():
            if self.last_request[action] < time.time() - self.check_redirect_cycle * 2:
                continue
            res = requests.get(self.intra_url + action + '/status')
            status = json.loads(res.text)
            if status['exec'][0] + status['lender'] + status['renter'] > 0:
                continue

            if action not in self.renter_lender_info.keys() or len(self.renter_lender_info[action].keys()) == 0:
                redirect_info = {'node': inter_url, 'action': action}
                try:
                    res = requests.post(head_url + '/redirect', json=redirect_info)
                except Exception as e:
                    print('e:', e)

            if action in self.lender_renter_info:
                for renter in self.lender_renter_info[action].keys():
                    self.renter_lender_info[renter].pop(action)
                self.lender_renter_info.pop(action)

            if action in self.renter_lender_info:
                for lender in self.renter_lender_info[action].keys():
                    self.lender_renter_info[lender].pop(action)
                self.renter_lender_info.pop(action)


# Ip config.
inter_port = 5000
intra_port = 5001
# hostname = socket.gethostname()
hostname = '0.0.0.0'
inter_url = socket.gethostbyname(hostname) + ':' + str(inter_port)
intra_url = 'http://0.0.0.0' + ':' + str(intra_port) + '/'
head_url = 'http://0.0.0.0:5100'

# An inter-controller instance.            
controller = inter_controller(intra_url,
                              '/home/openwhisk/sosp/Pagurus/interaction_controller/build_file/aws_packages.json')

# a Flask instance.
proxy = Flask(__name__)

# database
db_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
db_name = 'inter_results'
db_server = couchdb.Server(db_url)
if db_name in db_server:
    db_server.delete(db_name)
db = db_server.create(db_name)


# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    params = inp['params']
    controller.last_request[action_name] = time.time()
    # print('listen:', action_name, params)
    start = time.time()
    request_id = uuid.uuid4().hex
    url = controller.intra_url + action_name + '/run'
    while True:
        try:
            res = requests.post(url, json={'request_id': str(request_id), 'data': params})
            if res.text == 'OK':
                break
        except Exception:
            time.sleep(0.01)
    end = time.time()
    db[request_id] = {'start': start, 'end': end, 'end-to-end': end - start}
    return ('OK', 200)


@proxy.route('/cold_start', methods=['POST'])
def cold_start():
    inp = request.get_json(force=True, silent=True)
    name = inp['action_name']
    if name not in controller.cold_start:
        controller.cold_start[name] = 0
    controller.cold_start[name] += 1
    return ('OK', 200)


@proxy.route('/have_lender', methods=['POST'])
def have_lender():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    controller.add_lender(action_name)
    controller.has_lender[action_name] = True
    # controller.print_info()
    return ('OK', 200)


@proxy.route('/no_lender', methods=['POST'])
def no_lender():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    controller.remove_lender(action_name)
    controller.has_lender[action_name] = False
    # controller.print_info()
    return ('OK', 200)


@proxy.route('/repack_image', methods=['POST'])
def repack_image():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    controller.repack(action_name)
    # controller.print_info()
    return ('action_' + action_name + '_repack', 200)


@proxy.route('/rent', methods=['POST'])
def rent():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    res = controller.schedule_lender(action_name)
    if res == None:
        # print('rent: no lender')
        return ('no lender', 200)
    else:
        # print ('rent: ', action_name, ' ', res[0], ' ', res[2])
        return (json.dumps({'id': res[1], 'port': res[2]}), 200)


# communication with head
@proxy.route('/load-info', methods=['GET'])  # need to install sar
def load_info():
    '''
    cpu = subprocess.Popen(['sar', '-u', '1', '1'], stdout=subprocess.PIPE, encoding='UTF-8')
    cpu_info = cpu.stdout.read()
    cpu_load = 100.0 - float(list(filter(None, cpu_info[cpu_info.find('Average'):].split(' ')))[-1])

    mem = subprocess.Popen(['sar', '-r', '1', '1'], stdout=subprocess.PIPE, encoding='UTF-8')
    mem_info = mem.stdout.read()
    mem_load = float(list(filter(None, mem_info[mem_info.find('Average'):].split(' ')))[3])  
    # maybe need to change 3 to 4
    '''
    mem_info = psutil.virtual_memory()
    mem_load = mem_info.used / mem_info.total * 100

    cpu_load = psutil.cpu_percent()

    net = subprocess.Popen(['sar', '-n', 'DEV', '1', '1'], stdout=subprocess.PIPE, encoding='UTF-8')
    net_info = net.stdout.read()
    net_load = list(filter(None, net_info.split('\n')))
    net_load = list(filter(lambda x: x.find('Average') != -1 and x.find('IFACE') == -1, net_load))  # 如果是特定网口的话，
    # and第二个条件为x.find(<name_of_port>) != -1
    rxkB, txkB = 0, 0
    for port in net_load:
        rxkB += float(list(filter(None, port.split(' ')))[4])
        txkB += float(list(filter(None, port.split(' ')))[5])

    # print('cpu load: {}%; mem load: {}%; net load: rx: {}kB/s, tx: {}kB/s'.format(round(cpu_load, 2), mem_load, rxkB, txkB))
    node = dict()
    node['cpu'] = cpu_load
    node['mem'] = mem_load
    node['net'] = (rxkB + txkB) / 1000 * 100
    ret = dict()
    ret[inter_url] = node
    return (json.dumps(ret), 200)


def periodical_repack():
    gevent.spawn_later(controller.repack_period, periodical_repack)
    controller.periodical_repack()
    print(controller.repack_info)


@proxy.route('/lender-info', methods=['GET'])  # need to install sar
def lender_info():
    containers = controller.get_lender_list()
    return (json.dumps({'node': inter_url, 'containers': containers}), 200)


def init():
    # for action in controller.all_packages.keys():
    #    controller.generate_base_image(action)
    # controller.repack(action)
    # periodical_repack()
    # for action in controller.repack_info:
    #    print(action, controller.repack_info[action])
    '''
    cnt = {}
    for k1 in controller.repack_info:
        for k2 in controller.repack_info[k1]:
            if k2 not in cnt:
                cnt[k2] = 0
            cnt[k2] += 1
    # print(cnt)
    cnt2 = {}
    for i in range(30):
        cnt2[i] = 0
    for k in cnt:
        cnt2[cnt[k]] += 1
    print(cnt2)
    print(cnt2.values())
    '''
    # process = subprocess.Popen(['sudo', '/root/anaconda3/bin/python3', '/root/gls/intraaction_controller/proxy.py', str(intra_port)])
    server = WSGIServer(('0.0.0.0', inter_port), proxy)
    server.serve_forever()


def check_redirect():
    print('######### begin to check redirect.')
    controller.check_redirect()
    gevent.spawn_later(controller.check_redirect_cycle, check_redirect)


def update_repack():
    print('########## update_repack begin.')
    for lender in list(controller.repack_info.keys()):
        controller.repack(lender, repack_updating=True)
    gevent.spawn_later(controller.update_repack_cycle, update_repack)


if __name__ == '__main__':
    init()
    # gevent.spawn(init)
    # gevent.spawn_later(controller.update_repack_cycle, update_repack)
    # gevent.spawn_later(controller.check_redirect_cycle, check_redirect)
    # gevent.wait()
