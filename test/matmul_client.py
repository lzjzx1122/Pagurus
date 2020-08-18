from gevent import monkey
monkey.patch_all()
import gevent
import requests
import json
import sys
import time

count = 0
t1 = 1 / 10
count1 = 90 * 10
t2 = 1 / 8
count2 = count1 + 90 * 8

def test():
    global count
    global count1
    global count2
    global t1
    global t2
    id = count
    count += 1
    if count < count1:
        gevent.spawn_later(t1, test)
    elif count < count2:
        gevent.spawn_later(t2, test)
    start = time.time()
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"matmul", "params": {'param':2000}})
    end = time.time()
    print(id, start, end, end - start)


'''
t = int(time.time()) + 5
for _ in range(90):
    time.sleep(t - time.time())
    t += 1
    print("now:", time.time())
    for i in range(10):
        gevent.spawn(test)
    #gevent.sleep(0.5)

t = int(time.time()) + 5
for _ in range(90):
    time.sleep(t - time.time())
    t += 1
    print("now:", time.time())
    for i in range(8):
        gevent.spawn(test)
#    gevent.sleep(0.5)
'''
gevent.spawn(test)
gevent.wait()
