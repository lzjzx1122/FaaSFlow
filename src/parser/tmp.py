from gevent import monkey
monkey.patch_all()
import gevent
import requests

def rand():
    url = 'http://0.0.0.0:18001/run/rand'
    parameters = {}
    request_id = 'rand_1'
    res = requests.post(url, json = {"request_id": request_id, "data": parameters})

def cube():
    url = 'http://0.0.0.0:18001/run/cube'
    parameters = {'x': 3}
    request_id = 'cube_1'
    res = requests.post(url, json = {"request_id": request_id, "data": parameters})

def square():
    url = 'http://0.0.0.0:18001/run/square'
    parameters = {'x': 3}
    request_id = 'square_1'
    res = requests.post(url, json = {"request_id": request_id, "data": parameters})

gevent.joinall([gevent.spawn(square), gevent.spawn(cube)])

