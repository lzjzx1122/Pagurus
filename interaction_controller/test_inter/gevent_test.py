from gevent import monkey
monkey.patch_all()
import requests
import threading
import time
import gevent
import random

count = 0

def test():
    global count
    i = count
    count += 1
    start = time.time()
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"linpack", "params": {'param': 1000}})
    end = time.time()
    print(i, " ", start, " ", end, " ", end - start)

for _ in range(20):
    gevent.spawn(test)
    gevent.sleep(0.1)

gevent.sleep(60)

for _ in range(20):
    gevent.spawn(test)
    gevent.sleep(5)

gevent.wait()

