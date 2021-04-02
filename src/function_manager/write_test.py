import asyncio
import time
import string
import random
import aiofiles
import threading
import gevent
import couchdb

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = f'http://{username}:{password}@127.0.0.1:5984/'
db_name = 'test'

 if db_name in self.db_server:
            db = self.db_server[db_name]
        else:
            db = self.db_server.create(db_name)

dir = '/var/run/workflow_results/'
#dir = 'data/'
async def open_file(file):
    async with aiofiles.open(dir + file, mode='w') as f:
        await f.write()
    
async def open_all_files(files):
    tasks = []
    for file in files:
        task = asyncio.ensure_future(open_file(file))
        tasks.append(task)
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    
files = ['file1_', 'file2_', 'file3_', 'file4_', 'file5_', 'file6_', 'file7_', 'file8_', 'file9_', 'file10_']
sizes = [10000, 10199, 19919, 11991, 9999, 10000, 10199, 19091, 11990, 9999]

def write1():
    for i in range(10):
        file = files[i]
        size = sizes[i]
        with open(dir + file, 'w') as f:
            result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = size))
            f.write(result)

def write2():
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(open_all_files(files))

def read_file(file):
    with open(dir + file, mode='r') as f:
        content = f.read()
        print(len(content))
    
def read3():
    threads = []
    for file in files:
        t = threading.Thread(target=read_file, args=(file,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":    
    start_time = time.time()
    #write()
    #for i in range(10):
    write1()
    duration = time.time() - start_time
    print("duration:", duration)