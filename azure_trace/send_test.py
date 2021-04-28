from gevent import monkey
monkey.patch_all()
import gevent
import time
import json
import requests
import sys

def send_request(action, time_):
    # print('send to', exper[i]['name'], time_, time.time())
    url = "http://0.0.0.0:5000/listen"
    requests.post(url, json = {"action_name": action, "params": {'runtime': 1}})

print('send 0')
send_request('utility4', 0)
print('end 0')
