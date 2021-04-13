import asyncio
import time
import string
import random
import aiofiles
import threading
import gevent
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

def write1():
    for i in range(len(files)):
        file = files[i]
        size = sizes[i]
        with open(dir + file, 'w') as f:
            f.write(rand(size))

async def open_file(file, size):
    async with aiofiles.open(dir + file, mode='w') as f:
        await f.write(rand(size))
    
async def open_all_files(files):
    tasks = []
    for i in range(len(files)):
        task = asyncio.ensure_future(open_file(files[i], sizes[i]))
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)
    
def write2():
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(open_all_files(files))

def write_file(file, size):
    with open(dir + file, mode='w') as f:
        f.write(rand(size))
 
def write3():
    threads = []
    for i in range(len(files)):
        t = threading.Thread(target=write_file, args=(files[i],sizes[i],))
        threads.append(t)
        #t.start()

    for t in threads:
        t.start()

    for t in threads:
        t.join()

def write_db1():
    for i in range(20):
        db[files[i]] = {"value": rand(sizes[i])}

async def write_db(k, v):
    db[k] = v
    
async def write_all_dbs(files):
    tasks = []
    for i in range(len(files)):
        task = asyncio.ensure_future(write_db(files[i], {"value": rand(sizes[i])}))
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)

def write_db2():
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(write_all_dbs(files))

def write_db_thread(k, v):
    db[k] = v
 
def write_db3():
    threads = []
    for i in range(len(files)):
        t = threading.Thread(target=write_db_thread, args=(files[i], {"value": rand(sizes[i])},))
        threads.append(t)
        #t.start()

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":    
    start_time = time.time()
    write1()
    duration = time.time() - start_time
    print("duration:", duration)
