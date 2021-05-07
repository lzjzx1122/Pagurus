import gevent
import psutil
import time
import uuid
import couchdb
import os
import sys

os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/memory")
db_server = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984/')
if 'overhead' in db_server:
    db_server.delete('overhead')
db = db_server.create('overhead')

inter = psutil.Process(int(sys.argv[1]))
intra = psutil.Process(int(sys.argv[2]))

def run():
    gevent.spawn_later(6, run)
    inter_mem = inter.memory_percent()
    intra_mem = intra.memory_percent()
    inter_cpu = inter.cpu_percent()
    intra_cpu = intra.cpu_percent()
    # print({'time': time.time(), 'inter_memory': inter_mem, 'intra_mem': intra_mem, 'inter_cpu': inter_cpu, 'intra_cpu': intra_cpu})
    db[uuid.uuid4().hex] = {'time': time.time(), 'inter_memory': inter_mem, 'intra_memory': intra_mem, 'inter_cpu': inter_cpu, 'intra_cpu': intra_cpu}

gevent.spawn_later(1, run)
gevent.wait()
