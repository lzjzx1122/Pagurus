import requests
import json
import sys
import time


for i in range(int(sys.argv[1])):
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"disk", "params": {"bs":2048,"count":50000}})
    print(res.text)
