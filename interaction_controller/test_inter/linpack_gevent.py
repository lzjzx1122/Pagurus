from gevent import monkey
monkey.patch_all()
import requests
import gevent
import json
import sys
import time

count = 0
def test():
    global count
    i = count
    count += 1
    start = time.time()
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"linpack", "params": {'param': 100}})
    end = time.time()
    print(i, " ", start, " ", end, " ", end - start)

for _ in range(10):
    gevent.spawn(test)
    gevent.sleep(0.1)

gevent.wait()
