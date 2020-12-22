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
import numpy as np
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import requests
import socket

class inter_controller():
    def __init__(self, intra_url, package_path):
        self.intra_url = intra_url
        self.renter_lender_info = {} #{'renter A': {'lender B': cos, 'lender C':cos}}
        self.lender_renter_info = {} #{'lender A': {'renter B': cos, 'renter C':cos}}
        self.repack_info = {} #{'lender A': {'renter B': cos, 'renter C':cos}}
        self.repack_packages = {} #{'lender A': {'lib A':'ver A', 'lib B': 'ver B'}}
        self.all_packages = {}
        self.repacking = {} #{'action_name', True / False}
        self.package_path = package_path
        self.load_packages()
        
    def print_info(self):
        #print('----------------------------------------------------')
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
        
    def remove_lender(self, lender):
        if lender in self.lender_renter_info:
            for renter in list(self.lender_renter_info[lender].keys()):
                self.renter_lender_info[renter].pop(lender)
            self.lender_renter_info.pop(lender)    

    def add_lender(self, lender):
        while (lender in self.repacking) and (self.repacking[lender] == True):
            gevent.sleep(0)

        renters = self.repack_info[lender]
        self.lender_renter_info[lender] = renters
        for (k, v) in renters.items():
            if k not in self.renter_lender_info.keys():
                self.renter_lender_info.update({k: {lender: v}})
            else:
                self.renter_lender_info[k].update({lender: v})

    def choose_renters(self, lender, share_action_number=5):
        all_packages = self.all_packages.copy()
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
            if tmp == 0 :
                sim[candidate] = 1
            else:
                sim[candidate] = np.dot(lender_vector, candidate_vector) / tmp
        
        renters = dict()
        requirements = dict()
        while len(sim) > 0 and share_action_number > 0:
            renter = max(sim, key = sim.get)
            for (p, v) in all_packages[renter].items():
                requirements.update({p: v}) 
                renters.update({renter: sim[renter]})
                share_action_number -= 1
            sim.pop(renter)
        
        return renters, requirements

    def check_image(self, requirements, file_path):
        if os.path.exists(file_path) == False:
            return False
        file_read = open(file_path, 'r').readlines()
        if len(file_read) != len(requirements):
            return False
        for line in file_read:
            l = line.replace('\n', '').replace('\r', '')
            lib, version = None, None
            if '==' in l:
                l_split = l.split('==')
                lib = l_split[0]
                version = l_split[1]
            else:
                lib = l
                version = 'default'
            if (lib not in requirements) or (version != requirements[lib]):
                return False
        return True

    def generate_base_image(self, action_name):
        requirements = self.all_packages[action_name]
        
        save_path = 'images_save/' + action_name + '/'
        # file_path = save_path + 'requirements.txt'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # file_write = open(file_path, 'w')
        requirement_str = ''
        for requirement in requirements:
            # file_write.writelines(requirement + '\n')
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
        # file_path = save_path + 'requirements.txt'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # if self.check_image(requirements, file_path):
        #    return
        
        self.remove_lender(action_name)
        
        if repack_updating == True:
            while True:
                try:
                    url = self.intra_url + action_name + '/repack'
                    res = requests.post(url)
                    if res.text == 'OK':
                        break
                except Exception:
                    time.sleep(0.01)
        self.repacking[action_name] = True
        
        # file_write = open(file_path, 'w')
        requirement_str = ''
        for requirement in requirements:
            # file_write.writelines(requirement + '\n')
            requirement_str += ' ' + requirement

        with open(save_path + 'Dockerfile', 'w') as f:
            f.write('FROM action_{}\n'.format(action_name))
            # f.write('COPY pip.conf /etc/pip.conf\n')
            # for renter in renters.keys():
            #    f.write('COPY {}.zip /proxy/actions/action_{}.zip\n'.format(renter, renter))
            if requirement_str != '':
                f.write('RUN pip3 --no-cache-dir install{}'.format(requirement_str)) 
       
        # os.system('cd {} && cp ../../actions/pip.conf .'.format(save_path))
        # for renter in renters.keys():
        #    os.system('cd {} && cp ../../actions/{}.zip .'.format(save_path, renter))
        os.system('cd {} && docker build --no-cache -t action_{}_repack .'.format(save_path, action_name))
        
        self.repacking[action_name] = False

    def repack(self, action_name, repack_updating=False, share_action_number=5):
        renters, requirements = self.choose_renters(action_name, share_action_number)
        #print('get_renters: ', renters, requirements)
        self.generate_repacked_image(action_name, renters, requirements, repack_updating)
        self.repack_info[action_name] = renters        
        self.repack_packages[action_name] = requirements 
        return renters

    def schedule_renter(self, action_name):
        if action_name in self.renter_lender_info.keys() and len(self.renter_lender_info[action_name]) > 0:
            lender = max(self.renter_lender_info[action_name], key = self.renter_lender_info[action_name].get) 
            try:
                res = requests.get(self.intra_url + action_name + '/lend')               
                if res.text == 'no lender':
                    return None
                else:
                    res_dict = json.loads(res.text)
                    return lender, res_dict['id'], res_dict['port']
            except Exception:
                return None
        else:
            return None

    def get_lender_list(self):
        ret = []
        for lender in self.lender_renter_info:
            tmp = {}
            tmp['name'] = lender
            tmp['packages'] = self.repack_packages[lender]
            ret.append(tmp)
        return ret

    def check_sim(self):
        for i in list(self.renter_lender_info):
            try:
                res = requests.get(self.intra_url + i + '/status')
                res_dict = json.loads(res.text)
                # print('container:', i, res_dict['exec'][1], res_dict['lender'], res_dict['renter'])
                if res_dict['exec'][1] + res_dict['lender'] + res_dict['renter'] > 0:
                    continue
            except Exception:
                pass
            
            if len(self.renter_lender_info[i].values()) == 0: 
                action_delete_info = dict()
                action_delete_info['name'] = i
                action_delete_info['packages'] = self.all_packages[i]
                tmp = [action_delete_info]
                
                while True:
                    try:
                        # print('try:', head_url + '/redirect')
                        res = requests.post(head_url + '/redirect', json={inter_url:tmp})
                        if res.text == 'OK':  
                           break
                    except Exception as e:
                        print('e:', e)
                        time.sleep(0.01)
                '''
                url = 'http://0.0.0.0:' + str(controller.action_info[action][0]) + '/end'
                while True:
                    try:
                        res = requests.post(url)
                        if res.text == 'OK':
                            break
                    except Exception:
                        time.sleep(0.01)
                '''
                if i in self.lender_renter_info:
                    for renter in self.lender_renter_info[i].keys():
                        self.renter_lender_info[renter].pop(i)
                    self.lender_renter_info.pop(i)    

                for lender in self.renter_lender_info[i].keys():
                    self.lender_renter_info[lender].pop(i)
                self.renter_lender_info.pop(i)
                
                if i in self.repack_info:
                    self.repack_info.pop(i)

# Ip config.
inter_port = 5000
intra_port = 5001
hostname = socket.gethostname()
inter_url = socket.gethostbyname(hostname) + ':' + str(inter_port)
intra_url = 'http://0.0.0.0' + ':' + str(intra_port) + '/'
head_url = 'http://0.0.0.0:5100'

# An inter-controller instance.            
controller = inter_controller(intra_url, 'build_file/packages.json')
print(controller.choose_renters('linpack'))
print(controller.choose_renters('video'))

# a Flask instance.
proxy = Flask(__name__)

update_repack_cycle = 60 * 30
check_similarity_cycle = 60
request_id_count = 0

# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    params = inp['params']
    print('listen:', action_name, params)    
    global request_id_count
    request_id_count += 1
    request_id = request_id_count
    url = controller.intra_url + action_name + '/run'
    while True:
        try:
            res = requests.post(url, json = {'request_id': str(request_id), 'data': params})
            if res.text == 'OK':
                break
        except Exception:
            time.sleep(0.01)       
    return ('OK', 200)

@proxy.route('/have_lender', methods=['POST'])
def have_lender():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    controller.add_lender(action_name)
    controller.print_info()
    return ('OK', 200)

@proxy.route('/no_lender', methods=['POST'])
def no_lender():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    controller.remove_lender(action_name)
    controller.print_info()
    return ('OK', 200)

@proxy.route('/repack_image', methods=['POST'])
def repack_image():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    controller.repack(action_name)
    controller.print_info()
    return ('action_' + action_name + '_repack', 200)

@proxy.route('/rent', methods=['POST'])
def rent():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    res = controller.schedule_renter(action_name)
    if res == None:
        print('rent: no lender')
        return ('no lender', 200)
    else:
        print ('rent: ', action_name, ' ', res[0], ' ', res[2])
        return (json.dumps({'id': res[1], 'port': res[2]}), 200)

# communication with head 
@proxy.route('/load-info', methods=['GET']) # need to install sar
def load_info():
    cpu = subprocess.Popen(['sar', '-u', '1', '1'], stdout=subprocess.PIPE, encoding='UTF-8')
    cpu_info = cpu.stdout.read()
    cpu_load = 100.0 - float(list(filter(None, cpu_info[cpu_info.find('Average'):].split(' ')))[-1])

    mem = subprocess.Popen(['sar', '-r', '1', '1'], stdout=subprocess.PIPE, encoding='UTF-8')
    mem_info = mem.stdout.read()
    mem_load = float(list(filter(None, mem_info[mem_info.find('Average'):].split(' ')))[3])  
    # maybe need to change 3 to 4

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

@proxy.route('/lender-info', methods=['GET']) # need to install sar
def lender_info():
    ret = dict()
    ret[inter_url] = controller.get_lender_list()
    return (json.dumps(ret), 200)

def init():
    process = subprocess.Popen(['sudo', '/home/openwhisk/anaconda3/bin/python3', '../intraaction_controller/proxy.py', str(intra_port)])
    for action in controller.all_packages.keys():
        controller.generate_base_image(action)
    controller.print_info()
    server = WSGIServer(('0.0.0.0', inter_port), proxy)
    server.serve_forever()

def check_similarity():
    print('############################### begin to check similarity')
    controller.check_sim()
    gevent.spawn_later(check_similarity_cycle, check_similarity)

def update_repack():
    print('############################### update_repack begin')
    controller.load_packages()
    
    for lender in list(controller.repack_info.keys()):
        controller.repack(lender, True)
    
    controller.renter_lender_info.clear()
    for lender in list(controller.lender_renter_info.keys()):
        renters = controller.repack_info[lender]
        controller.lender_renter_info[lender] = renters
        for renter in renters:
            if renter not in controller.renter_lender_info:
                controller.renter_lender_info[renter] = {lender: renters[renter]}
            else:
                controller.renter_lender_info[renter].update({lender: renters[renter]})
    
    gevent.spawn_later(update_repack_cycle, update_repack)

if __name__ == '__main__':
    pass
    # init()
    # gevent.spawn(init)
    # gevent.spawn_later(update_repack_cycle, update_repack)
    # gevent.spawn_later(check_similarity_cycle, check_similarity)
    # gevent.wait()    