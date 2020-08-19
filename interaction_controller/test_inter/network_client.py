import requests
import json
import sys
import time

#start = time.time()
#url = "http://0.0.0.0:5000/admin"
#res = requests.post(url, json = {"action_name":"float_operation", "packages": {'numpy': 'default'}})
#end = time.time()
#print("admin:", start, " ", end, " ", end - start)


for i in range(int(sys.argv[1])):
    url = "http://0.0.0.0:5000/listen"
    res = requests.post(url, json = {"action_name":"network", "params": {'name':'5mb'}})
    print(res.text)
