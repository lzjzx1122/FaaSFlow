import gevent
import psutil
import time
import uuid
import couchdb
import os
import sys

db_server = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984/')
if 'overhead' in db_server:
    db_server.delete('overhead')
db = db_server.create('overhead')

managers = [psutil.Process(int(sys.argv[1])), psutil.Process(int(sys.argv[2]))]
mems = []
cpus = []

def run():
    gevent.spawn_later(1, run)
    mem = (managers[0].memory_percent() + managers[0].memory_percent()) / 2
    cpu = (managers[0].cpu_percent() + managers[1].cpu_percent()) / 2
    print('time: ', time.time(), 'mem: ', mem, 'cpu: ', cpu)
    mems.append(mem)
    cpus.append(cpu)
    # db[uuid.uuid4().hex] = {'time': time.time(), 'inter_memory': inter_mem, 'intra_memory': intra_mem, 'inter_cpu': inter_cpu, 'intra_cpu': intra_cpu}

def avg():
    gevent.spawn_later(10, avg)
    print('average mem: ', sum(mems) / len(mems), 'average cpu: ', sum(cpus) / len(cpus))

gevent.spawn_later(1, run)
gevent.spawn_later(10, avg)
gevent.wait()