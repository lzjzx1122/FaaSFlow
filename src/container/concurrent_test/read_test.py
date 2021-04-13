import asyncio
import time
import string
import random
import aiofiles
import threading
import gevent

dir = '/var/run/workflow_results/'
#dir = 'data/'
async def open_file(file):
    async with aiofiles.open(dir + file, mode='r') as f:
        content = await f.read()
        print(len(content))
    return len(content)

async def open_all_files(files):
    tasks = []
    for file in files:
        task = asyncio.ensure_future(open_file(file))
        tasks.append(task)
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    
files = ['file1', 'file2', 'file3', 'file4', 'file5', 'file6', 'file7', 'file8', 'file9', 'file10']

def write():
    sizes = [1000090] * 10
    for i in range(10):
        file = files[i]
        size = sizes[i]
        with open(dir + file, 'w') as f:
            result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = size))
            f.write(result)

def read1():
    for file in files:
        with open(dir + file, 'r') as f:
            result = f.read()
            print(len(result))

def read2():
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
    read1()
    duration = time.time() - start_time
    print("duration:", duration)