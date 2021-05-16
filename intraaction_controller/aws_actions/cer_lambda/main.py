import time
import requests
import xlsxwriter
import pandas
import numpy

def main(param):
    start = time.time()

    runtime = param['runtime']
    time.sleep(runtime)

    latency = time.time() - start
    return {"latency": latency}
 