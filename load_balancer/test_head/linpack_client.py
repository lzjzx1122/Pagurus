import requests
import json
import sys

for i in range(int(sys.argv[1])):
    url = "http://0.0.0.0:5100/action"
    res = requests.post(url, json = {"action":"linpack", "params": {'timeout':10, 'param': 1000}})
    print(res.text, res.ok)
