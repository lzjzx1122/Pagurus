import requests
import json

url = "http://0.0.0.0:5000/listen"
res = requests.post(url, json = {"action_name":"linpack", "params": {'param': 1000}})
print(res.text)
