import requests
import gevent

head_url = "http://172.23.164.202:5000/action"

action_list = {'couchdb_test':{}, 'linpack':{'param':1000}, 'matmul':{'param':2000}, 'image':{}, 'disk':{"bs":2048,"count":50000}, 'markdown2html':{}}

def test(action, param):
    global head_url
    res = requests.post(head_url, json = {'action':action, 'params':param})

for _ in range(5):
    for action in action_list:
        gevent.spawn(test(action, action_list[action]))
        gevent.sleep(0.1)
    gevent.sleep(60)

gevent.wait()

