import gevent
import psutil
import time
import uuid
import couchdb
import os

os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/memory")
db_server = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984/')
db = db_server.create('memory')

def run():
    gevent.spawn_later(1, run)
    info = psutil.virtual_memory()
    total = info.total
    used = info.used
    cpu = psutil.cpu_percent()
    print('cpu', cpu)
    db[uuid.uuid4().hex] = {'time': time.time(), 'memory': used / total, 'cpu':cpu}

gevent.spawn_later(1, run)
gevent.wait()