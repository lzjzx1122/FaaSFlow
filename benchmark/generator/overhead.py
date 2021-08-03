import gevent
import psutil
import time
import uuid
import couchdb
import os
import sys
import pandas as pd

# db_server = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984/')
# if 'overhead' in db_server:
#     db_server.delete('overhead')
# db = db_server.create('overhead')

managers = [psutil.Process(int(sys.argv[1]))]
mems = []
cpus = []
times = []

def run():
    gevent.spawn_later(0.5, run)
    mem = managers[0].memory_percent()
    cpu = managers[0].cpu_percent()
    # print('time: ', time.time(), 'mem: ', mem, 'cpu: ', cpu)
    mems.append(mem)
    cpus.append(cpu)
    times.append(time.time())
    # db[uuid.uuid4().hex] = {'time': time.time(), 'inter_memory': inter_mem, 'intra_memory': intra_mem, 'inter_cpu': inter_cpu, 'intra_cpu': intra_cpu}

def avg():
    gevent.spawn_later(10, avg)
    print('average mem: ', sum(mems) / len(mems), 'average cpu: ', sum(cpus) / len(cpus))
    df = pd.DataFrame({'time': times, 'mem': mems, 'cpu': cpus})
    df.to_csv('overhead.csv', index=False)

gevent.spawn_later(1, run)
gevent.spawn_later(10, avg)
gevent.wait()