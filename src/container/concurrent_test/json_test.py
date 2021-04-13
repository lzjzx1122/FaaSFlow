import asyncio
import time
import string
import random
import aiofiles
import threading
import gevent
import json
import couchdb

couchdb_url = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
db_server = couchdb.Server(couchdb_url)
db_name = 'test'
if db_name in db_server:
    db_server.delete(db_name)
db = db_server.create(db_name)

dir = './'
files = ['file1', 'file2', 'file3', 'file4', 'file5', 'file6', 'file7', 'file8', 'file9', 'file10', 'file1_', 'file2_', 'file3_', 'file4_', 'file5_', 'file6_', 'file7_', 'file8_', 'file9_', 'file10_']
sizes = [100000, 100199, 109919, 119091, 99099, 100000, 100199, 190091, 110990, 99099, 43433, 43434, 112333, 32421, 32424, 55555, 66666, 77777, 22222, 111111]

for i in range(len(files)):
    sizes[i] = sizes[i] * 10

def rand(size):
    return 'a' * size

def write_file(path, size):
    with open(path, "w") as f:
        json.dump({'value': rand(size)}, f)

def write1():
    for i in range(len(files)):
        file = files[i]
        size = sizes[i]
        write_file(file, size)
 
def write2():
    threads = []
    for i in range(len(files)):
        t = threading.Thread(target=write_file, args=(files[i],sizes[i],))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def read_file(path):
    with open(path, mode='r') as f:
        content = f.read()
        print(len(content))

def read1():
    for i in range(len(files)):
        file = files[i]
        read_file(file)
 
def read2():
    threads = []
    for i in range(len(files)):
        t = threading.Thread(target=read_file, args=(files[i],))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":    
    start_time = time.time()
    read1()
    duration = time.time() - start_time
    print("duration:", duration)
