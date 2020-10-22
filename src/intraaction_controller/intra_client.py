from gevent import monkey
monkey.patch_all()
import requests
import threading
import time
import gevent
import random

def test():
    i = random.randint(0, 1000000)
    data = {
        'request_id': str(i),
        'data': {
            'param': 10
        }
    }
    start = time.time()
    r = requests.post('http://127.0.0.1:5001/run', json=data)
    end = time.time()
    print(i, start, end, end - start)

for _ in range(100):
    gevent.spawn(test)
    gevent.sleep(0.1)

gevent.sleep(10)

for _ in range(100):
    gevent.spawn(test)
    gevent.sleep(0.5)

gevent.wait()
