import requests
import json
import sys

for i in range(int(sys.argv[1])):
    url = "http://202.120.38.79:8218/action"
    res = requests.post(url, json = {"action":"linpack", "params": {'param': 1000}})
    print(res.text, res.ok)
