import requests
import json
import sys

for i in range(int(sys.argv[1])):
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"matmul", "params": {'param':2000}})
    print(res.text)
