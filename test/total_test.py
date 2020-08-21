from gevent import monkey
monkey.patch_all()
import requests
import gevent
import time

head_url = "http://172.23.164.207:5000/action"

action_list = {'linpack':{'param':1000}, 'image':{}, 'couchdb_test':{}, 'matmul':{'param':2000}, 'disk':{"bs":2048,"count":50000}, 'markdown2html':{}}

#action_list = {'markdown2html': {}}
ans1 = []
ans2 = []

def test(action, param):
	global head_url
	start = time.time()
	res = requests.post(head_url, json = {'action':action, 'params':param})
	end = time.time()
	print(action, start, end, end - start)
	ans1.append(action)
	ans2.append(end - start)

for _ in range(5):
    for action in action_list:
        gevent.spawn(test(action, action_list[action]))
        gevent.sleep(2)
    gevent.sleep(70)

gevent.wait()

for x in ans1:
	print(x)

for x in ans2:
	print(x)
