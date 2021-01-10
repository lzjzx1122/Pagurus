from gevent import monkey
monkey.patch_all()
import gevent
import json
import requests
import sys

parameters = \
{   
    "couchdb_test": {},
    "disk": {"bs":8192, "count": 200000},
    "float_operation": {"param": 1000000},
    "image": {},
    "k-means": {},
    "linpack": {"param": 5000},
    "map_reduce": {},
    "markdown2html": {},
    "matmul": {},
    "network": {"name": "5mb"},
    "video": {}
}

exper = json.loads(open(sys.argv[1], encoding='utf-8').read())
# print(exper)

def send_request(i):
    print('send to', exper[i]['name'])
    #url = "http://0.0.0.0:5100/action"
    #action = exper[i]['name']
    #requests.post(url, json = {"action": action, "params": {'timeout': exper[i]['runtime'], 'param': parameters[action]}})
'''    
def run(time_):
    if time_ < 1439:
        gevent.spawn_later(1, run, time_ + 1)
    for i in range(1):
        for _ in range(exper[i]['invo'][time_]):
            gevent.spawn(send_request, i)
'''
def run(time_):
    if time_ < 10:
        gevent.spawn_later(0.2, run, time_ + 1)
    for i in range(11):
        for _ in range(exper[i]['invo'][time_ // 5]):
            gevent.spawn(send_request, i)


run(0)

gevent.wait()
