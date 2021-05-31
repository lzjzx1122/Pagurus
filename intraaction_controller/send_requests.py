from gevent import monkey
monkey.patch_all()
import gevent
import time
import json
import random
import requests
import sys
import uuid

def send_func(action, runtime):
    print('send to', action, runtime)
    url = "http://0.0.0.0:5001/" + action + "/run"
    requests.post(url, json = {"request_id": str(uuid.uuid4().hex), "data": {'runtime': runtime}})


# def send_app(app):
#     for func in app:
#         start_time = float(app[func]['start_time'])
#         runtime = float(app[func]['duration'])
#         gevent.spawn_later(start_time, send_func, func, runtime)
       
f = json.loads(open('./build_file/aws_packages.json', encoding='utf-8').read())
for _ in f.keys():
    send_func('cer_lambda', 0.1)
    time.sleep(3)