import requests
import os,time

def main(param):
    file_name = param['name']
    #上传文件到服务器
    file = {'file': open(file_name,'rb')}
    start_time = time.time()
    r = requests.post('http://10.2.64.8:12345/upload', files=file)
    latency = time.time()-start_time
    print('latency :',latency)
    return{"latency":latency}

