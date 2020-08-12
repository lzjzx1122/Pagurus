import requests
import json
import sys

for i in range(int(sys.argv[1])):
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"float_operation", "params": {'param': 1000000}})
    print(res.text)
