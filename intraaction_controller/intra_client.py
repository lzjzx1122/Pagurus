import requests
import threading
import time
import gevent
import random

def test():
    i = random.randint(0, 1000000)
    data = {
        'request_id': str(i),
        'data': {
            'param': 1000
        }
    }
    r = requests.post('http://127.0.0.1:5000/run', json=data)
    print(i, r.ok)

while True:
    gevent.spawn(test)
    gevent.sleep(0.1)
