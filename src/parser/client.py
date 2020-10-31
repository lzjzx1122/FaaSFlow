from gevent import monkey
monkey.patch_all()
import gevent
import json
import requests

def do(i):
    url = 'http://0.0.0.0:18000/listen'
    res = requests.post(url, json = {"request_id": str(i)}) 
    print(i, res)

total = 10
pool = []
for i in range(total):
    pool.append(gevent.spawn(do, i))
    gevent.sleep(0.5)

gevent.joinall(pool)
