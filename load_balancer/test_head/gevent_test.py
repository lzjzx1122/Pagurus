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
    url = "http://0.0.0.0:5100/action"
    res = requests.post(url, json = {"action":"linpack", "params": {'param': 1000}})
    end = time.time()
    print(i, " ", start, " ", end, " ", end - start)

def test2():
    global count
    i = count
    count += 1
    start = time.time()
    url = "http://0.0.0.0:5100/action"
    res = requests.post(url, json = {"action":"float_operation", "params": {'param': 1000000}})
    end = time.time()
    print(i, " ", start, " ", end, " ", end - start)

def test3():
    global count
    i = count
    count += 1
    start = time.time()
    url = "http://0.0.0.0:5100/action"
    res = requests.post(url, json = {"action":"matmul", "params": {'param':2000}})
    end = time.time()
    print(i, " ", start, " ", end, " ", end - start)

    
test()

for _ in range(20):
    gevent.spawn(test)
    gevent.sleep(0.1)

gevent.sleep(10)

for _ in range(100):
    gevent.spawn(test)
    gevent.sleep(5)

#gevent.sleep(10)

test2()

for _ in range(20):
    gevent.spawn(test2)
    gevent.sleep(0.1)

gevent.wait()

