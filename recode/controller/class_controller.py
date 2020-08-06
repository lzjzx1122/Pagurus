import os
import docker
import time
import asyncio
import queue
import couchdb
from threading import Thread
from class_repack import repack_controller 
from flask import Flask, request
import sys
sys.path.append('../')
from container.class_action import action_create
#from multiprocessing import Value,Process,Array

def asynci(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        return wrapper

class node_controller():
    def __init__(self,node_id):
        self.node_id = node_id
        self.action_object = {} #{"action_name": [action_object, max_containers]}
        self.repack_controller = repack_controller()
        self.renter_lender_info = {} #{"renter A": {lender B: cos, lender C:cos}}
        self.action_counter = {}
    
    def action_info_update(self,action_obj=None):
        if action_obj and (action_obj.action_name not in self.action_object.keys()):
            self.action_object.update({action_obj.action_name:action_obj})
        for (k1,v1) in self.action_object.items():
            if v1.current_containers == 0:
                self.action_object.pop(k1)
                self.renter_lender_info.pop(k1)

    def renter_lender_info_add(self,lender,renter_dict):
        for (k1,v1) in renter_dict.items():
            if k1:
                if k1 not in self.renter_lender_info.keys():
                    self.renter_lender_info.update({k1:{lender:v1}})
                else:self.renter_lender_info[k1].update({lender:v1})
            else:pass

    def action_repack(self,action_name,docker_file_json,packages_json,share_action_number=2):
        self.action_info_update()
        self.repack_controller.packages_reload()
        lender,renter = self.repack_controller.action_repack(action_name,docker_file_json,packages_json,share_action_number)
        self.repack_controller.image_save()
        #inform intra 
        return lender, renter

    def action_scheduler(self,action_obj):
        if action_obj.action_name in self.renter_lender_info.keys():
            lender_obj = max(self.renter_lender_info[action_obj.action_name], key=self.renter_lender_info[action_obj.action_name].get) 
            if (self.action_object[lender_obj].share_count > 0) and (action_obj.current_containers < action_obj.max_containers):
                #inform lender delete container
                #inform renter add container
                
                # action_obj.renter_instance_info = self.action_list[lender_obj].lender_instance_info[self.action_list[lender_obj].share_count-1]
                # #加容器状态检查
                # self.action_list[lender_obj].lender_instance_info[self.action_list[lender_obj].share_count-1] = None
                # self.action_list[lender_obj].share_count -= 1
                # self.action_list[lender_obj].current_containers -= 1
                # action_obj.current_containers += 1
                lender_sign = True
        else:lender_sign = False
        return lender_sign

            
test = node_controller(1)
test.action_repack('image',{"pillow":"default"},{"pillow":"default","numpy":"default"},3)
test.action_repack('linpack',{"pillow":"default"},{"numpy":"default"},3)
#test.action_scheduler('float_operation')
print(test.renter_lender_info)


# A couchdb to store the results of action.
couch = couchdb.Server("http://openwhisk:openwhisk@localhost:5984/")
db = couch.create("action_results")
# A queue to store user requests.
action_queue = queue.Queue()
# a Flask instance.
proxy = Flask(__name__)
user_path = "/home/openwhisk/pagurus/actions"
port_number_start = 18080 # not sure!
max_share_count = 2 # not sure!

# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    arrival_time = time.time()
    obj = None
    if action_name not in test.action_object:
        # action1: [port_number_start, port_number_start + max_containers_1)
        # action2: [port_number_start + max_containers_1, port_number_start + max_containers_[1, 2])
        # ......
        # actionN: [port_number_start + max_containers_[1, 2, ..., N-1], port_number_start + max_containers_[1, 2, ..., N])
        max_containers = inp['max_containers']
        # user must apply max_containers in the first request
        obj = action_create(port_number_start, user_path, action_name, max_containers, max_share_count)
        port_number_start += max_containers
        test.action_object[action_name] = [obj, max_containers]
        test.action_counter[action_name] = 0
        obj.first_arrival_time = arrival_time
        obj.total_requests = 1
    else:
        obj = test.action_object[action_name][0]
        obj.total_requests += 1
        if obj.total_requests % 10 == 1:
            obj.lambd = (arrival_time - obj.first_arrival_time) / (obj.total_requests - 1)

    action_queue.put({'action_name': action_name, 'arrival_time': arrival_time})


#def view_func(doc):
#    yield doc['end_time'], doc

#for i in range(10):
#    rand = random.randint(1, 100)
#    doc = {'action_name': 'test', 'arrival_time': rand, 'begin_time': rand, 'end_time': rand, 'duration': rand, 'result': rand}
#    db.save(doc)

# Run forever.
while True:
    for id in db:
        doc = db[id]
        action_name = doc['action_name']
        arrival_time = doc['arrival_time']
        begin_time = doc['begin_time']
        end_time = doc['end_time']
        result = doc['result']

        obj = test.action_object[action_name][0]
        obj.finished_requests += 1
        obj.Qos_satisfied_requests += (end_time - arrival_time <= obj.Qos_time)
        obj.exec_time += end_time - begin_time

        test.action_counter[action_name] += 1
        if test.action_counter[action_name] % 10 == 1:
            obj.mu = obj.finished_requests / obj.exec_time
            obj.Qos_value_cal = obj.Qos_satisfied_requests / obj.finished_requests
            
        db.delete(doc)
