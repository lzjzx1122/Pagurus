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


# communication with head ########################################
@proxy.route('/load-info', methods=['GET']) # need to install sar
def load_info():
    cpu = subprocess.Popen(["sar", "-u", "1", "1"], stdout=subprocess.PIPE, encoding='UTF-8')
    cpu_info = cpu.stdout.read()
    cpu_load = 100.0 - float(list(filter(None, cpu_info[cpu_info.find("Average"):].split(' ')))[-1])

    mem = subprocess.Popen(["sar", "-r", "1", "1"], stdout=subprocess.PIPE, encoding='UTF-8')
    mem_info = mem.stdout.read()
    mem_load = float(list(filter(None, mem_info[mem_info.find("Average"):].split(' ')))[4])

    net = subprocess.Popen(["sar", "-n", "DEV", "1", "1"], stdout=subprocess.PIPE, encoding='UTF-8')
    net_info = net.stdout.read()
    net_load = list(filter(None, net_info.split('\n')))
    net_load = list(filter(lambda x: x.find('Average') != -1 and x.find('IFACE') == -1, net_load))  # 如果是特定网口的话，
    # and第二个条件为x.find(<name_of_port>) != -1
    rxkB, txkB = 0, 0
    for port in net_load:
        rxkB += float(list(filter(None, port.split(' ')))[4])
        txkB += float(list(filter(None, port.split(' ')))[5])

    # print("cpu load: {}%; mem load: {}%; net load: rx: {}kB/s, tx: {}kB/s".format(round(cpu_load, 2), mem_load, rxkB, txkB))
    node = dict()
    node['cpu'] = cpu_load
    node['mem'] = mem_load
    node['net'] = (rxkB + txkB) / 1000 * 100 
    ret = dict()
    ret[node_ip] = node
    return ret

@proxy.route('/lender-info', methods=['GET']) # need to install sar
def lender_info():
    ret = dict()
    ret[node_ip] = test.lender_list()
    return ret

def main():
    server = WSGIServer(('0.0.0.0', 7899), proxy)
    server.serve_forever()

def check_similarity():
    while 1:
        print("begin to check similarity")
        test.check_sim()
        time.sleep(60*30)

if __name__ == '__main__':
    try:
        _thread.start_new_thread( main, ( ) )
        _thread.start_new_thread( check_similarity, ( ) )
    except:
        print('thread start fail')

    while 1:
        pass
