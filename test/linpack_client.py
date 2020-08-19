from gevent import monkey
monkey.patch_all()
import gevent
import requests
import json
import sys
import time

count = 0
t1 = 4 / 10
count1 = 90 * 10 / 4
t2 = 4 / 8
count2 = count1 + 90 * 8 / 4
t3 = 4 / 5
count3 = count2 + 90 * 5 / 4

def test():
        global count
        global count1
        global count2
        global t1
        global t2
        global t3
        id = count
        count += 1
        if count < count1:
                gevent.spawn_later(t1, test)
        elif count < count2:
                gevent.spawn_later(t2, test) 
        elif count < count3:
                gevent.spawn_later(t3, test)
        start = time.time()
        url = "http://0.0.0.0:5000/listen"
        res = requests.post(url, json = {"action_name":"linpack", "params": {'param':1000}})
        end = time.time()
        print(id, start, end, end - start)

gevent.spawn(test)
gevent.wait()
