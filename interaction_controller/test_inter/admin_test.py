import requests
import gevent

def linpack_admin():
    try:
        res = requests.post("http://0.0.0.0:5000/admin", json = {"action_name":"linpack", "packages":{"numpy":"default"}})
        print(res)
        print(res.text)
    except Exception as e:
        print(e)

def float_admin():
    try:
        res = requests.post("http://0.0.0.0:5000/admin", json = {"action_name":"float_operation", "packages":{"numpy":"default"}})
        print(res)
        print(res.text)
    except Exception as e:
        print(e)

def matmul_admin():
    try:
        res = requests.post("http://0.0.0.0:5000/admin", json = {"action_name":"matmul", "packages":{"numpy":"default"}})
        print(res)
        print(res.text)
    except Exception as e:
        print(e)

gevent.spawn(linpack_admin)
#gevent.spawn(float_admin)
#gevent.spawn(matmul_admin)
gevent.wait()
