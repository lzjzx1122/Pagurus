import os
import docker
import time
import asyncio
from threading import Thread
from class_repack import repack_controller 
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
    
    def action_info_update(self,action_obj=None):
        if action_obj and (action_obj.action_name not in self.action_list.keys()):
            self.action_list.update({action_obj.action_name:action_obj})
        for (k1,v1) in self.action_list.items():
            if v1.current_containers == 0:
                self.action_list.pop(k1)
                self.renter_lender_info.pop(k1)

    def renter_lender_info_add(self, renter_name,lender_name_dict):
        self.renter_lender_info.update({renter_name:lender_name_dict})

    def action_repack(self,action_name,docker_file_json,packages_json,share_action_number=2):
        self.repack_controller.packages_reload()
        lender,renter = self.repack_controller.action_repack(action_name,docker_file_json,packages_json,share_action_number)
        self.repack_controller.image_save()
        return lender, renter

    def action_image_save(self):
        pass

    def action_scheduler(self):
        pass
        
test = node_controller(1)
test.action_repack('image',{"pillow":"default"},{"pillow":"default"},3)