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
# mems = []
# cpus = []
# times = []
mem_max = 0
cpu_max = 0

def run():
    global mem_max, cpu_max
    gevent.spawn_later(0.01, run)
    try:
        mem = managers[0].memory_percent()
        cpu = managers[0].cpu_percent()
        mem_max = max(mem_max, mem)
        cpu_max = max(cpu_max, cpu)
        print('mem: ', mem, 'cpu: ', cpu)
    # print('time: ', time.time(), 'mem: ', mem, 'cpu: ', cpu)
        # mems.append(mem)
        # cpus.append(cpu)
    except Exception as e:
        print('MEM_MAX: ', mem_max * 61.9 * 1024 * 1024 * 0.01, 'CPU_MAX: ', cpu_max)
    # times.append(time.time())
    # avg()
    # db[uuid.uuid4().hex] = {'time': time.time(), 'inter_memory': inter_mem, 'intra_memory': intra_mem, 'inter_cpu': inter_cpu, 'intra_cpu': intra_cpu}

# def avg():
#     gevent.spawn_later(10, avg)
#     print('average mem: ', sum(mems) / len(mems), 'average cpu: ', sum(cpus) / len(cpus))
#     df = pd.DataFrame({'time': times, 'mem': mems, 'cpu': cpus})
#     df.to_csv('overhead.csv', index=False)

gevent.spawn(run)
# gevent.spawn_later(10, avg)
gevent.wait()