import requests
import threading
import time
import random

i = 0

def test():
    global i
    data = {
        'request_id': str(i),
        'data': {
            'param': 1000
        }
    }
    i += 1
    r = requests.post('http://127.0.0.1:5000/run', json=data)
    print(i-1, r.ok)

while True:
    threading.Thread(target=test).start()
    time.sleep(0.5)
