import sys,os
import pycurl
import json
import time
import re
import asyncio
from io import BytesIO
from functools import partial
from multiprocessing import Pool
from multiprocessing import Process,Array,Value

#status_list = Value('d',0)

def curl_create(port_number):
    url = "http://0.0.0.0:"+str(port_number)+"/checkstatus"

    c = pycurl.Curl()
    b = BytesIO()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.CUSTOMREQUEST,"POST")
    #c.setopt(pycurl.HTTPHEADER,["Content-Type: application/json"])
    c.setopt(pycurl.SSL_VERIFYHOST, False)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    #c.setopt(pycurl.POSTFIELDS,data)
    return c,b

def action_post(c,b):
    #start_time = time.time()
    c.perform()
    temp = b.getvalue().decode()
    b.write('\n'.encode('utf-8'))
    listemp = re.split('\n',temp)
    res = json.loads(listemp[-1])
    #if "response" in res.keys():
    #    print(res["response"]["result"]["latency"])
    return res
    #print(status_list.value)
    #time_passed = time.time() - start_time
    #print(time_passed)
    #wait = 0.02-time_passed
    #if wait > 0:
    #    time.sleep(wait)
    #else:
    #    time.sleep(tmp_wait)

#action_post(0.02,18080)
