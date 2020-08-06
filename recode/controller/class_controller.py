import os
import docker
import time
import asyncio
import queue
import couchdb
from threading import Thread
from class_repack import repack_controller 
from flask import Flask, request
from class_action import action_create
#from multiprocessing import Value,Process,Array

def asynci(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        return wrapper

class node_controller():
    def __init__(self,node_id):
        self.node_id = node_id
        self.repack_controller = repack_controller()
        self.action_list = {} #{"renter A":A_obj}
        self.renter_lender_info = {} #{"renter A": {lender B: cos, lender C:cos}}
        self.action_object = {} #{"action_name": action_object}
    
    def action_info_update(self,action_obj=None):
        if action_obj and (action_obj.action_name not in self.action_list.keys()):
            self.action_list.update({action_obj.action_name:action_obj})
        for (k1,v1) in self.action_list.items():
            if v1.current_containers == 0:
                self.action_list.pop(k1)
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
        #inform intra to generate lender container
        self.renter_lender_info_add(lender,renter)
        return lender, renter

    def action_scheduler(self,action_obj):
        if action_obj.action_name in self.renter_lender_info.keys():
            lender_obj = max(self.renter_lender_info[action_obj.action_name], key=self.renter_lender_info[action_obj.action_name].get) 
            if (self.action_list[lender_obj].share_count > 0) and (action_obj.current_containers < action_obj.max_containers):
                action_obj.renter_instance_info = self.action_list[lender_obj].lender_instance_info[self.action_list[lender_obj].share_count-1]
                #加容器状态检查
                self.action_list[lender_obj].lender_instance_info[self.action_list[lender_obj].share_count-1] = None
                self.action_list[lender_obj].share_count -= 1
                self.action_list[lender_obj].current_containers -= 1
                action_obj.current_containers += 1
        else:pass

            
test = node_controller(1)
test.action_repack('image',{"pillow":"default"},{"pillow":"default","numpy":"default"},3)
test.action_repack('linpack',{"pillow":"default"},{"numpy":"default"},3)
test.action_scheduler('float_operation')
print(test.renter_lender_info)


# A couchdb to store the results of action.
couch = couchdb.Server("http://openwhisk:openwhisk@localhost:5984/")
db = couch.create("action_results")
# A queue to store user requests.
action_queue = queue.Queue()
# a Flask instance.
proxy = Flask(__name__)
action_count = 0
user_path = "/home/openwhisk/pagurus/actions"
port_number_start = 18080 # not sure!
max_containers = 10 # not sure!
share_count = 2 # not sure!

# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    arrival_time = time.time()
    
    obj = None
    if action_name not in test.action_object:
        # action1: [port_number_start, port_number_start + max_containers)
        # action2: [port_number_start + max_containers, port_number_start + max_containers * 2)
        # ......
        # actionN: [port_number_start + max_containers * (N - 1), port_number_start + max_containers * N)
        obj = action_create(port_number_start + action_count * max_containers, user_path, action_name, max_containers, share_count)
        action_count += 1
        test.action_object[action_name] = obj
        obj.first_arrival_time = arrival_time
        obj.total_requests = 1
    else:
        obj = test.action_object[action_name]
        obj.total_requests += 1
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

        obj = test.action_object[anction_name]
        obj.finished_requests += 1
        obj.Qos_satisfied_requests += (end_time - arrival_time <= obj.Qos_time)
        obj.Qos_value_cal = obj.Qos_satisfied_requests / obj.finished_requests
        obj.exec_time += end_time - start_time
        obj.mu = obj.finished_requests / obj.exec_time
        
        db.delete(doc)
