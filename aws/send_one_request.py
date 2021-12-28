import requests

url = "http://0.0.0.0:5000/listen"
requests.post(url, json={"action_name": 'cs_bot', "params": {'runtime': 0.1}})
