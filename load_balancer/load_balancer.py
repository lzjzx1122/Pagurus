from gevent import monkey
monkey.patch_all()
import gevent 
import subprocess
from flask import Flask, request, Response
import requests
import threading
import time
import numpy as np
from gevent.pywsgi import WSGIServer
import sys

class LoadBalancer:
	def __init__(self, server_addr_list):
		self.server_list = list()  # {server1, server2, ...}
		self.route_table = dict()  # {action_name: [1, 3, 4] } ps:node refer to the index of server in server_list
		self.lender_list = dict()
		self.load_info = dict()  # {node_index: {cpu: xx%, mem: xx%, net: xx%, max: xx%}
        #self.lender_list_lock = threading.Lock()  # lock for update lender_list
        #self.load_info_lock = threading.Lock()  # lock for update server load status
		for addr in server_addr_list:
			self.server_list.append(addr)

	def check_server_threshold(self, server_node, threshold):  # check if server load is over threshold        """
		if server_node < 0 or server_node >= len(self.server_list):
			return False
		load_info = self.load_info.get(server_node, {})
		if len(load_info) == 0:
			return True
		cpu_load = load_info.get("cpu", 0)
		mem_load = load_info.get("mem", 0)
		net_load = load_info.get("net", 0)
		return cpu_load < threshold and mem_load < threshold and net_load < threshold


	def get_new_node(self, action_name, nodes):
		server_count = len(self.server_list)
		hash_node = hash(action_name) % server_count
		for node in range(hash_node, hash_node+server_count):
			new_node = node % server_count
            # print('get_new_node:', new_node, nodes)	
			if new_node not in nodes and self.check_server_threshold(new_node, 80):
				return new_node
		return None
        
	def route(self, action_name, params):
		if action_name not in self.route_table.keys() or len(self.route_table[action_name]) == 0: # new action
			self.route_table[action_name] = []
			new_node = self.get_new_node(action_name, self.route_table[action_name])
			print('new_node:', new_node)
			if new_node == None:
				raise Exception('no available server to add new action for {}'.format(action_name))
			self.route_table[action_name].append(new_node)
		ret = Response(status=404)
		sent = False
		for node in self.route_table[action_name] :
			if self.check_server_threshold(node, 80):
				ret = self.send_request(node, action_name, params)
				sent = True
				break
		if sent:
			return ret
		else:
			new_node = self.get_new_node(action_name, self.route_table[action_name])
			if new_node != None:
				self.route_table[action_name].append(new_node)
				ret = self.send_request(new_node, action_name, params)
			return ret

# action in route table?
# no: add action to route, compute parent node, determine load, if ok, parent node -> current node, else check parent+1
# yes: determine current node(list), if has, route to current node;else turn to parent node, determine parent
# node load, if yes, route to parent node, parent node -> current node, else, check parent_node+1。。。

	def send_request(self, server_node, action_name, params):
		url = self.server_list[server_node]
		action_data = {
			"action_name": action_name,
			"params": params,
		}
		res = requests.post('http://' + url + '/listen', json=action_data)
		if res.ok:
			return Response(status=200)
		else:
			return Response(status=404)

	def get_load_info(self, server_node):
		if server_node < 0 or server_node >= len(self.server_list):
			raise IndexError
		server = self.server_list[server_node]
		load_info = requests.get('http://' + server + '/load-info')
		if load_info.ok:
			load_info = load_info.json()
			print('load_info:', load_info)
			max_load = max(load_info[server]['cpu'], load_info[server]['mem'], load_info[server]['net'])
			load_info[server].update({'max': max_load})
            #self.load_info_lock.acquire()
			self.load_info.update({server_node: load_info[server]})
			#self.load_info_lock.release()
	
	def get_lender_info(self, server_node):  # server_node is the one that don't need to get lender info
		if server_node < 0 or server_node >= len(self.server_list):
 			raise IndexError
		server = self.server_list[server_node] 
		res = requests.get('http://' + server + '/lender-info')
		if res.ok:
			res = res.json()
			#self.lender_list_lock.acquire()
			self.lender_list.update({server_node: res['containers']})
			#self.lender_list_lock.release()

	def update_load_info(self):
		pool = []
		for server_node in range(len(self.server_list)):
			pool.append(gevent.spawn(self.get_load_info, server_node))
		gevent.joinall(pool)

	def update_lender_info(self, server_nodes):
		pool = []
		for server_node in server_nodes:
			pool.append(gevent.spawn(self.get_lender_info, server_node))
		gevent.joinall(pool)

	def redirect(self, server_node, action_name):
		current_nodes = self.route_table[action_name]
		self.route_table[action_name] = list(filter(lambda x: x != server_node, current_nodes))
		new_node = self.get_new_node(action_name, current_nodes)
		if new_node != None:
			self.route_table[action_name].append(new_node)
		else:
			raise Exception('no available server to add new action for {}'.format(action_name))
		self.update_lender_info(self.route_table[action_name])
		tmp_list = []
		for server_node in self.route_table[action_name]:
			tmp_list.append((server_node, self.lender_list[server_node][action_name], self.load_info[server_node]['max']))
		tmp_list.sort(key=lambda el: (el[1], -el[2]), reverse=True)  # sort by containers
		if tmp_list[0][1] < 1:  # no match server, treat it as neutral stuffing
			tmp_list.sort(key=lambda el: (el[2], -el[1]))  # sort by load
		self.route_table[action_name] = list(map(lambda el: el[0], tmp_list))
		return Response(status=200)


load_balancer = LoadBalancer(['172.20.185.119:5000', '172.20.185.120:5000', '172.20.185.121:5000', '172.20.185.122:5000', '172.20.185.123:5000'])
#load_balancer = LoadBalancer(['172.20.185.122:5000'])
head = Flask(__name__)
head.debug = False

@head.route('/action', methods=["POST", "GET"])
def handle_action():
    action_data = request.get_json()
    # print("receive data:", action_data['action'])
    ret = load_balancer.route(action_data['action'], action_data['params'])
    return ('OK', 200)  # Response(status=200)


@head.route('/redirect', methods=["POST"])
def handle_redirect():
    redirect_info = request.get_json()
    server_addr = redirect_info['node']
    server_node = load_balancer.server_list.index(server_addr)
    if server_node == -1:
        return 404, 'server not found'
    action = redirect_info['action']
    print("redirect:", server_addr, action)
    load_balancer.redirect(server_node, action)
    return ('OK', 200)


@head.route('/route-table', methods=['GET'])
def route_table():
    return load_balancer.route_table


@head.route('/lender-list', methods=['GET'])
def lender_list():
    return load_balancer.lender_list


@head.route('/test', methods=['GET'])
def test():
    return request.get_json()


@head.route('/update-lender', methods=['GET', 'POST'])
def test1():
    load_balancer.update_lender_info([0, 1, 2])
    return Response(status=200)


@head.route('/update-load', methods=['GET', 'POST'])
def test2():
    load_balancer.update_load_info()
    return Response(status=200)

def init():
    server = WSGIServer('0.0.0.0:5100', head)
    server.serve_forever()

update_load_cycle = 5
def update_load():
    load_balancer.update_load_info()
    gevent.spawn_later(update_load_cycle, update_load)

if __name__ == '__main__':
    #init()
    gevent.spawn(init)
    gevent.spawn_later(update_load_cycle, update_load)
    gevent.wait()    
