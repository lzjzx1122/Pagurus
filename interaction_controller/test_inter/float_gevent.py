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
    res = requests.post(url, json = {"action_name":"float_operation", "params": {'param': 1000000}})
    end = time.time()
    print(i, " ", start, " ", end, " ", end - start)

for _ in range(20):
    gevent.spawn(test)
    gevent.sleep(0.1)

