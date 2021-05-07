from gevent import monkey
monkey.patch_all()
import gevent
import time
import json
import random
import requests
import sys

def send_func(action, runtime):
    print('send to', action, runtime)
    url = "http://0.0.0.0:5000/listen"
    requests.post(url, json = {"action_name": action, "params": {'runtime': runtime}})

def send_app(app):
    for func in app:
        start_time = float(app[func]['start_time'])
        runtime = float(app[func]['duration'])
        gevent.spawn_later(start_time, send_func, func, runtime)
       
f = json.loads(open('/root/sosp/Pagurus/interaction_controller/build_file/aws_packages.json', encoding='utf-8').read())
for _ in f.keys():
    send_func(_, 0.1)
    time.sleep(5)

