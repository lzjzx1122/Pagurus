from gevent import monkey
monkey.patch_all()
import gevent
import os
import signal
import time
from multiprocessing import Process
import subprocess
import requests
import threading

#action = 'video'
#i = 10
#node = '172.20.185.122'
#url = 'http://' + node + ':5002/' 
#print(url)
#res = requests.post(url + 'start', json = {'action': action, 'id': i})
# res = requests.post('http://172.20.185.122:5002/start', json = {'action': action, 'id': i})
 
actions = ["video", "network", "linpack", "disk", "float_operation", "k-means", "markdown2html", "matmul", "image", "map_reduce", "couchdb_test"]
nodes = ['172.20.185.119', '172.20.185.120', '172.20.185.121', '172.20.185.122', '172.20.185.123']
#nodes = ['172.20.185.122']
'''
os.system('python3 /root/Pagurus/load_balancer/init.py')
action = 'video'
i = 10
for node in nodes:
	url = 'http://' + node + ':5002/' 
	print(url)
	res = requests.post(url + 'start', json = {'action': action, 'id': i})
 
	#url = 'http://' + node + ':5000/'
	#req = 'curl ' + url + 'start -X POST -d \'{\"action\":\"' + action + '\", \"id\":\"' + str(i) + '\"}\''
	#print(req)
	#req = 'curl ' + url + 'listen -X POST -d \'{\"action_name\":\"' + action + '\"}\''
	#print(req)
	#os.system(req)
'''
def start(node, action, i):
	url = 'http://' + node + ':5002/' 
	requests.post(url + 'start', json = {'action': action, 'id': i})
	
def stop(node):
	url = 'http://' + node + ':5002/' 
	requests.get(url + 'stop')
	
for i in range(1, 6):
	for action in actions:
		os.system('python3 /root/Pagurus/load_balancer/init.py')
		pool = []
		for node in nodes:
			print('node:', node)
			pool.append(gevent.spawn(start, node, action, i))
		gevent.joinall(pool)
		head = subprocess.Popen(['python3', '/root/Pagurus/load_balancer/load_balancer.py'])
		time.sleep(30)
		dir = 'results/' + action + '/' + str(i)
		os.system('python3 run.py ' + dir + '/set.json')
		time.sleep(30)
		os.system('kill -9 ' + str(head.pid))
		for node in nodes:
			stop(node)
		dir = 'head_results/' + action + '/' + str(i) + '_'
		os.system('mkdir ' + dir)
		os.system('python3 get_results.py ' + dir)
		time.sleep(30)
