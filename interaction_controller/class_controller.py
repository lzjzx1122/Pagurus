from gevent import monkey
monkey.patch_all()
import os
import time
import docker
import asyncio
import queue
import couchdb
import subprocess
#import requests
import random
import json
import numpy as np
from threading import Thread, Lock
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import requests
import socket
import _thread

def asynci(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        return wrapper

class node_controller():
    def __init__(self, node_id):
        self.node_id = node_id
        self.renter_lender_info = {} #{"renter A": [lender B: cos, lender C:cos]}
        self.lender_renter_info = {} #{"lender A": [renter B: cos, renter C:cos]}
        self.repack_info = {} #{"lender A": [renter B: cos, renter C:cos]}
        self.action_info = {} #{"action_name": [port_number, process]}
        self.package_path = "build_file/packages.json"
        self.all_packages = {}
        self.info_lock = Lock()

    def print_info(self):
        print("----------------------------------------------------")
        print("lender_renter_info:")
        for lender in self.lender_renter_info:
            print(lender, end = ": ")
            for (renter, value) in self.lender_renter_info[lender].items():
                print(renter, " ", value, end = " ")
            print("")
        print("renter_lender_info:")
        for renter in self.renter_lender_info:
            print(renter, end = ": ")
            for (lender, value) in self.renter_lender_info[renter].items():
                print(lender, " ", value, end = " ")
            print("")

    def packages_reload(self):
        #self.info_lock.acquire()
        all_packages = open(self.package_path, encoding='utf-8')
        all_packages_content = all_packages.read()
        self.all_packages = json.loads(all_packages_content)
        #self.info_lock.release()
    
    def remove_lender(self, lender):
        self.info_lock.acquire()
        if lender in self.lender_renter_info:
            for renter in self.lender_renter_info[lender].keys():
                self.renter_lender_info[renter].pop(lender)
            self.lender_renter_info.pop(lender)    
        self.info_lock.release()

    def add_lender(self, lender):
        self.info_lock.acquire()
        renters = self.repack_info[lender]
        self.lender_renter_info[lender] = renters
        for (k, v) in renters.items():
            if k not in self.renter_lender_info.keys():
                self.renter_lender_info.update({k: {lender: v}})
            else:
                self.renter_lender_info[k].update({lender: v})
        self.info_lock.release()

    def get_renters(self, action_name, packages, share_action_number=2):
        all_packages_content = open(self.package_path, encoding='utf-8')
        all_packages = json.loads(all_packages_content.read())
        all_packages.pop(action_name)
        renters = {}
        candidates = {}
        requirements = {}
        for (k1, v1) in packages.items():
                for (k2, v2) in all_packages.items():
                    if (k1 in v2) and (v2[k1] != v1):
                        all_packages.pop(k2)
        packages_vector = []
        vector_x, vector_y = [], []
        for (k1,v1) in packages.items(): 
            for (k2,v2) in all_packages.items():
                if (k1 in v2) and (k2 not in candidates.keys()):
                    candidates[k2] = 0
                    packages_vector.extend(v2.keys())
                    packages_vector = list(set(packages_vector))
        #list all the packages that contain child set
        for x in packages_vector:
            if x in packages.keys():
                vector_x.append(1)
            else:
                vector_x.append(0)
        #calculate the vector_x
        for candidate in candidates.keys():
            for x in packages_vector:
                if x in all_packages[candidate].keys():
                    vector_y.append(1)
                else:
                    vector_y.append(0)    
            candidates[candidate] = (np.dot(vector_x, vector_y) / (np.linalg.norm(vector_x) * np.linalg.norm(vector_y)))
            vector_y = []
        #calculate the vector_y and cos distance
        #print ("candidates: ", action_name, " ", candidates)
        while len(candidates) > 0 and share_action_number > 0:
            renter = max(candidates, key = candidates.get)
            flag = True
            for (k, v) in all_packages[renter].items():
                if (k in requirements) and (requirements[k] != v):
                    flag = False
                    break
            if flag:
                for (k, v) in all_packages[renter].items():
                    requirements.update({k: v}) 
                renters.update({renter: candidates[renter]})
                share_action_number -= 1
            candidates.pop(renter)
        #print("renters: ", renters)
        return renters, requirements

    def check_image(self, requirements, file_path):
        if os.path.exists(file_path) == False:
            return False
        file_read = open(file_path, 'r').readlines()
        if len(file_read) != len(requirements):
            return False
        for line in file_read:
            lib, version = None, None
            if "==" in line:
                line_split = line.split("==")
                lib = line_split[0]
                version = line_split[1]
            else:
                lib = line
                version = "default"
            if (lib not in requirements) or (version != requirements[lib]):
                return False
        return True

    def image_base(self, action_name):
        all_dockerfiles_content = open('build_file/packages.json', encoding='utf-8')
        all_dockerfiles = json.loads(all_dockerfiles_content.read())
        requirements = all_dockerfiles[action_name]

        save_path = 'images_save/' + action_name + '/'
        file_path = save_path + 'requirements.txt'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_write = open(file_path, 'w')
        for requirement in requirements:
            file_write.writelines(requirement + '\n')

        with open(save_path + 'Dockerfile', 'w') as f:       
            f.write('FROM action_{}\n'.format(action_name))
            f.write('COPY {}.zip /proxy/actions/action_{}.zip\n'.format(action_name, action_name))
            f.write('COPY requirements.txt .\n')
            f.write('RUN pip3 install --no-cache-dir -r requirements.txt && rm requirements.txt')  
        
        os.system('cd {} && cp ../../actions/{}.zip . && docker build -t action_{} .'.format(save_path, action_name, action_name))

    def image_save(self, action_name, renters, requirements):  
        all_dockerfiles_content = open('build_file/packages.json', encoding='utf-8')
        all_dockerfiles = json.loads(all_dockerfiles_content.read())

        save_path = 'images_save/' + action_name + '_repack/'
        file_path = save_path + 'requirements.txt'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if self.check_image(requirements, file_path):
            return True

        file_write = open(file_path, 'w')
        for requirement in requirements:
            file_write.writelines(requirement + '\n')

        with open(save_path + 'Dockerfile', 'w') as f:
            f.write('FROM action_{}\n'.format(action_name))
            f.write('COPY {}.zip /proxy/actions/action_{}.zip\n'.format(action_name, action_name))
            f.write('COPY requirements.txt .\n')
            f.write('RUN pip3 install --no-cache-dir -r requirements.txt && rm requirements.txt') 
 
        os.system('cd {} && cp ../../actions/{}.zip . && docker build -t action_{}_repack .'.format(save_path, action_name, action_name))
        return False

    def action_repack(self, action_name, packages, share_action_number=2):
        renters, requirements = self.get_renters(action_name, packages, share_action_number)
        self.image_save(action_name, renters, requirements)

        self.info_lock.acquire()
        self.repack_info[action_name] = renters        
        self.info_lock.release()
        
        return renters

    def action_scheduler(self, action_name):
        if action_name in self.renter_lender_info.keys() and len(self.renter_lender_info[action_name]) > 0:
            lender = max(self.renter_lender_info[action_name], key = self.renter_lender_info[action_name].get) 
            #不超过max_containers由intra保证
            try:
                res = requests.get(url = "http://0.0.0.0:" + str(test.action_info[lender][0]) + "/lend")               
                if res.text == 'no lender':
                    return None
                else:
                    res_dict = json.loads(res.text)
                    return lender, res['id'], res['port']
            except Exception:
                return None
        else:
            return None

#inter-action controller            
test = node_controller(1)
test.packages_reload()
#action_list = ["disk", "linpack", "image"]
#for action in action_list:
#    test.action_repack(action, test.all_packages[action])
test.print_info()

# a Flask instance.
proxy = Flask(__name__)
test_lock = Lock()
container_port_number_count = 18081
port_number_count = 5001
request_id_count = 0
# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    params = inp['params']
    
    global test_lock
    test_lock.acquire()
    global request_id_count
    global port_number_count
    global container_port_number_count    
    request_id_count += 1
    request_id = request_id_count
    container_port_number = container_port_number_count
    need_init = False
    if action_name not in test.action_info:
        need_init = True
        #process = subprocess.Popen(['python3', 'tmp.py', action_name])
        process = subprocess.Popen(['python3', '../intraaction_controller/proxy.py', str(port_number_count)])
        #process = None
        test.action_info[action_name] = [port_number_count, process] 
        port_number_count += 1
        container_port_number_count += 10
    test_lock.release()

    if need_init:
        test.image_base(action_name)
        #print("need_init") 
        while True:
            try:
                url = "http://0.0.0.0:" + str(test.action_info[action_name][0]) + "/init"
                #print("init: ", url)
                res = requests.post(url, json = {"action": action_name, "pwd": action_name, "QOS_time": 0.3, "QOS_requirement": 0.95, "min_port": container_port_number, "max_container": 10})
                print("res: ", res)
                if res.text == 'OK':
                    break
            except Exception:
                time.sleep(0.01)       

    print ("listen: ", request_id, " ", action_name)

    while True:
        try:
            url = "http://0.0.0.0:" + str(test.action_info[action_name][0]) + "/run"
            res = requests.post(url, json = {"request_id": str(request_id), "data": params})
            if res.text == 'OK':
                break
        except Exception:
            time.sleep(0.01)       
    
    return ('OK', 200)

@proxy.route('/have_lender', methods=['POST'])
def have_lender():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    #print ("have_lender: ", action_name)
    test.add_lender(action_name)
    test.print_info()
    return ('OK', 200)

@proxy.route('/no_lender', methods=['POST'])
def no_lender():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    #print ("no_lender: ", action_name)
    test.remove_lender(action_name)
    test.print_info()
    return ('OK', 200)

@proxy.route('/repack_image', methods=['POST'])
def repack_image():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    print ("repack_image: ", action_name, " ", test.all_packages[action_name])
    test.action_repack(action_name, test.all_packages[action_name])
    test.print_info()
    return ("action_" + action_name + "_repack", 200)

@proxy.route('/rent', methods=['POST'])
def rent():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    res = test.action_scheduler(action_name)
    if res == None:
        return ('no renter', 200)
    else:
        print ("rent: ", action_name, " ", res[0], " ", res[2])
        return (json.dumps({"id": res[1], "port": res[2]}), 200)

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
