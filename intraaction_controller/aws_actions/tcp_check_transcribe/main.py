import time
import aws_requests_auth
import elasticsearch
import certifi
import chardet
import idna
import requests
import urllib3

def main(param):
    start = time.time()

    runtime = param['runtime']
    time.sleep(runtime)

    latency = time.time() - start
    return {"latency": latency}

