import os
import docker
import time
import asyncio
import queue
import couchdb
import subprocess
import requests
import random
from threading import Thread, Lock
from flask import Flask, request
from gevent.pywsgi import WSGIServer

def asynci(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        return wrapper

class node_controller():
    def __init__(self,node_id):
        self.node_id = node_id
        self.renter_lender_info = {} #{"renter A": [lender B: cos, lender C:cos]}
        self.lender_renter_info = {}
        self.action_info = {} #{"action_name": [port_number, process]}
        self.all_packages = {}
       
    def package_reload(self):
        all_packages = open('build_file/packages.json', sencoding='utf-8')
        all_packages_content = all_packages.read()
        self.all_packages = json.loads(all_packages_content)
    
    def remove_lender(self, lender):
        if lender in self.lender_renter_info:
            for renter in self.lender_renter_info[lender].keys():
                self.renter_lender_info[renter].pop(lender)
            self.lender_renter_info.pop(lender)    

    def renter_lender_info_add(self, lender, renters):
        self.lender_renter_info[lender] = renters
        for (k, v) in renters.items():
            if k not in self.renter_lender_info.keys():
                self.renter_lender_info.update({k: {lender: v}})
            else:
                self.renter_lender_info[k].update({lender: v})

    def get_renters(self, action_name, packages, share_action_number=2):
        all_packages_content = open('build_file/packages.json', encoding='utf-8')
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
            candidates[candidate] = (np.dot(vector_x,vector_y) / (np.linalg.norm(vector_x)*np.linalg.norm(vector_y)))
            vector_y = []
        #calculate the vector_y and cos distance
        while len(candidates) > 0 and share_action_number > 0:
            renter = max(candidates, key = candidates.get)
            flag = True
            for (k, v) in all_packages[renter]:
                if (k in requirements) and (reqirements[k] != v):
                    flag = False
                    break
            if flag:
                for (k, v) in all_packages[renter]:
                    requirements.update({k: v}) 
                renters.update({renter_id: candidates[renter_id]})
                share_action_number -= 1
            candidates.pop(renter_id)
        return renters, requirements

    def check_image(self, requirements, file_path):
        if os.path.exists(file_path) == False:
            return False
        file_read = open(file_path, 'r').readlines()
        if len(file_read) != len(requirement):
            return False
        for line in file_read:
            lib = None
            if "==" in line:
                line_split = line.split("==")
                lib = {line_split[0]: line_split[1]})
            else:
                lib = {line: "default"}
            if (lib[0] not in requirements) or (lib[1] != requirements[lib[0]]):
                return False
        return True

    def image_save(self, action_name, renters, requirements):  
        all_dockerfiles_content = open('build_file/docker_file.json', encoding='utf-8')
        all_dockerfiles = json.loads(all_dockerfiles_content.read())

        save_path = 'images_save/' + action_name + '/'
        file_path = save_path + 'requirements.txt'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if self.check_image(requirements, file_path):
            return True

        file_write = open(file_path, 'w')
        for requirement in save_requirements:
            file_write.writelines(requirement+'\n')

        with open(self.save_path + 'Dockerfile', 'w') as f:
            f.write('FROM lzjzx1122/python3action{}\n\n\
                    COPY requirements.txt /\n\n\
                    RUN pip3 install -r requirements.txt'.format(self.action_name))
        #os.system('cd {} && docker build -t lzjzx1122/python3action_pack_{} .'.format(self.save_path, self.action_name))
        return False

    def repack_image(self, action_name, packages, share_action_number=2):
        renters, requirements = self.get_renters(action_name, packages, share_action_number)
        self.image_save(action_name, renters)
        self.render_lender_info_update(action_name, renters)
        return renters

    def action_scheduler(self, action_name):
        if action_name in self.renter_lender_info.keys():
            lender = max(self.renter_lender_info[action_name], key = self.renter_lender_info[action_name].get) 
            #不超过max_containers由intra保证
            return lender
        return None

#inter-action controller            
test = node_controller(1)
test.reload()
# a Flask instance.
proxy = Flask(__name__)
lock = Lock()
port_number_count = 5000
request_id_count = 0
# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    data = inp['data']
    lock.require()
    if action_name not in test.action_info:
        port_number_count += 1
        #process = subprocess.Popen(['python3', '../intraaction_controller/proxy.py', str(port_number_count)])
        process = None
        test.action_info[action_name] = [port_number_count, process]
        url = "http://0.0.0.0:" + str(port_number_count) + "/init"
        res = None
        while res == None or res.text != 'OK'
            res = requests.post(url, data = {"action": action_name, "pwd": action_name, "QOS_time": 0.3, "QOS_requirement": 0.95, "max_container": 10})
            time.sleep(0.01)  
    global require_id_count
    require_id_count += 1
    request_id = require_id_count
    lock.release()

    url = "http://0.0.0.0:" + str(test.action_info[action_name][0]) + "/run"
    #res = requests.post(url, data = {"request_id": request_id, "data" = data})
    print ("listen: ", request_id, " ", data)
    return ('OK', 200)

@proxy.route('/lender_empty', methods=['POST'])
def repack_image():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    print ("lender_empty: ", lender_empty)
    test.remove_lender(action_name)
    return ('OK', 200)

@proxy.route('/repack_image', methods=['POST'])
def repack_image():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    print ("repack_image: ", action_name, " ", test.all_packages[action_name])
    test.repack_image(action_name, test.all_packages[action_name])
    return ("../interaction_controller/images_save/" + action_name, 200)

@proxy.route('/rent', methods=['POST'])
def repack_image():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    lender = test.action_scheduler(action_name)
    print ("rent: ", renter, " ", lender)
    if lender == None:
        return ('NO', 200)
    else:
        return (lender, 200)

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
