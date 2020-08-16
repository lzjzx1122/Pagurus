from gevent import monkey
monkey.patch_all()
import subprocess
from flask import Flask, request, Response
import requests
import threading
import time
import numpy as np
from gevent.pywsgi import WSGIServer
import sys


def cal_similarity(action_packages, lender_packages):
    vector_a, vector_l = [], []
    for package in lender_packages.keys():
        if package in action_packages.keys():
            vector_a.append(1)
        else:
            vector_a.append(0)
        vector_l.append(1)
    return np.dot(vector_a, vector_l) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_l))


class LoadBalancer:
    def __init__(self, server_addr_list):
        # self.server_list = dict()  # {hash_key: server_addr}
        self.server_list = list()  # {server1, server2, ...}
        self.route_table = dict()  # {action_name: {hash_node: 1, route_nodes: [1, 3, 4]} } ps:node refer to the index of server in server_list
        self.lender_list = dict()  # {node_index: [{name: lender1, packages: {}}, {name:lender2, packages: {}}] }
        self.load_info = dict()  # {node_index: {cpu: xx%, mem: xx%, net: xx%, max: xx%}
        self.lender_list_lock = threading.Lock()  # lock for update lender_list
        self.load_info_lock = threading.Lock()  # lock for update server load status
        for addr in server_addr_list:
            self.server_list.append(addr)

    def check_server_threshold(self, server_node, threshold):  # check if server load is over threshold
        """
        :param server_node: index of server in server_list
        :param threshold: the checking threshold
        :return: true if over the threshold, false otherwise
        """
        if server_node < 0 or server_node >= len(self.server_list):
            return False
        load_info = self.load_info.get(server_node, {})
        if len(load_info) == 0:
            return True
        cpu_load = load_info.get("cpu", 0)
        mem_load = load_info.get("mem", 0)
        net_load = load_info.get("net", 0)
        return cpu_load < threshold and mem_load < threshold and net_load < threshold

    def add_action(self, action_name):  # add a new action to route_table
        self.route_table.update({action_name: {}})
        server_count = len(self.server_list)
        hash_node = hash(action_name) % server_count
        route_nodes = []
        for node in range(hash_node, hash_node+server_count):
            if self.check_server_threshold(node % server_count, 70):
                route_nodes.append(node % server_count)
        if len(route_nodes) == 0:  # no available server to add new action
            raise Exception('no available server to add new action for {}'.format(action_name))
        self.route_table[action_name].update({'hash_node': hash_node, 'route_nodes': route_nodes})
        return route_nodes

    def route(self, action_name, params):
        route_nodes = []
        if action_name not in list(self.route_table.keys()):  # new action
            try:
                route_nodes = self.add_action(action_name)
            except Exception as e:
                print(e)
        else:  # find its route table
            table = self.route_table.get(action_name, {})
            if len(table) == 0:  # the table is empty, handle it as a new action
                # server = list(self.server_list.keys())[hash(action_name) % len(self.server_list.keys())]
                # self.route_table.update({action_name: [server]})
                self.route_table.pop(action_name)  # remove from route table
                route_nodes = self.add_action(action_name)
            else:
                route_nodes = table.get('route_nodes', [])
                if len(route_nodes) == 0:  # no route node
                    self.route_table.pop(action_name)
                    route_nodes = self.add_action(action_name)
        ret = Response(status=404)
        for node in route_nodes:
            if self.check_server_threshold(node, 90):
                ret = self.send_request(node, action_name, params)
                break

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
            max_load = max(load_info[server]['cpu'], load_info[server]['mem'], load_info[server]['net'])
            load_info[server].update({'max': max_load})
            self.load_info_lock.acquire()
            self.load_info.update({server_node: load_info[server]})
            self.load_info_lock.release()

    def get_lender_info(self, server_node):  # server_node is the one that don't need to get lender info
        if server_node < 0 or server_node >= len(self.server_list):
            raise IndexError
        server = self.server_list[server_node]
        lender_info = requests.get('http://' + server + '/lender-info')
        print(lender_info.status_code)
        if lender_info.ok:
            # lenders = list(lender_info[server].values())
            lender_info = lender_info.json()
            print(lender_info)
            self.lender_list_lock.acquire()
            self.lender_list.update({server_node: lender_info[server]})
            self.lender_list_lock.release()

    def update_load_info(self):
        # lock = threading.Lock()
        # sys_info = dict()  # {"hash_key: {cpu: xx%, mem: xx%, net: xx%}}
        for server_node in range(len(self.server_list)):
            thread = (threading.Thread(target=self.get_load_info(server_node)))
            thread.start()
            thread.join()
        print(self.load_info)

    def update_lender_info(self, server_nodes):
        for server_node in server_nodes:
            thread = threading.Thread(target=self.get_lender_info(server_node))
            thread.start()
            thread.join()
        print(self.lender_list)

# get redirect action info, compute similarity of each node, if max > 20%
# check node satisfy 70%, if ok, redirect, else subMax
# else(max < 20%): check load info list, choose one that has lowest load

    def cal_server_similarity(self, packages, server_node):
        lenders = self.lender_list.get(server_node, {})
        max_sim = 0
        for lender in lenders:
            # lender_name = lender['name']
            lender_packages = lender['packages']
            conflict = False
            for package, version in packages:
                if (package in list(lender_packages.keys())) and (version != lender_packages[package]):
                    conflict = True
            if conflict:
                continue
            sim = cal_similarity(packages, lender_packages)
            max_sim = sim if max_sim < sim else max_sim
        return max_sim

    def redirect(self, server_node, action_data):
        self.update_load_info()
        action_name = action_data['name']
        packages = action_data['packages']
        current_nodes = self.route_table[action_name]['route_nodes']
        self.route_table[action_name]['route_nodes'] = list(filter(lambda x: x != server_node, current_nodes))
        if len(self.route_table[action_name]['route_nodes']) == 0:  # no available nodes, update load and add action
            self.update_load_info()
            self.route_table.pop(action_name)
            self.add_action(action_name)
        self.update_lender_info(self.route_table[action_name]['route_nodes'])
        tmp_list = []
        for server_node in self.route_table[action_name]['route_nodes']:
            sim = self.cal_server_similarity(packages, server_node)
            tmp_list.append((server_node, sim, self.load_info[server_node]['max']))
        tmp_list.sort(key=lambda el: (el[1], -el[2]), reverse=True)  # sort by similarity
        if tmp_list[0][1] < 0.2:  # no match server, treat it as neutral stuffing
            tmp_list.sort(key=lambda el: (el[2], -el[1]))  # sort by load, then by sim
        self.route_table[action_name]['route_nodes'] = list(map(lambda el: el[0], tmp_list))
        return Response(status=200)


def get_server_info(net_bandwidth):
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

    ret = dict()
    ret['cpu'] = round(cpu_load, 2)
    ret['mem'] = mem_load
    ret['net'] = round((rxkB + txkB) / net_bandwidth * 100, 2)
    # print ret
    return ret


load_balancer = LoadBalancer(['10.2.64.8:5000'])#, '0.0.0.0:5002', '0.0.0.0:5003'])
head = Flask(__name__)
head.debug = False


@head.route('/action', methods=["POST", "GET"])
def handle_action():
    action_data = request.get_json()
    ret = load_balancer.route(action_data['action'], action_data['params'])
    return ('OK', 200)  # Response(status=200)


@head.route('/redirect', methods=["POST"])
def handle_redirect():
    data = request.get_json()
    server_addr = list(data.keys())[0]
    server_node = load_balancer.server_list.index(server_addr)
    if server_node == -1:
        # print(server_addr, file=sys.stderr)
        return 404, 'server not found'
    action_data = data[server_addr][0]
    print("redirect:", server_addr, action_data)
    #load_balancer.redirect(server_node, action_data)
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


if __name__ == '__main__':
    server = WSGIServer('0.0.0.0:5100', head)
    server.serve_forever()
    # head.run(host='0.0.0.0', port=5000)
    # load_balancer.update_load_info()
