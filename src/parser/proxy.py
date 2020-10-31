from gevent import monkey
monkey.patch_all()
import gevent
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import couchdb
import requests
import json
import os
import sys
import time
from ServerlessBase import ServerlessBase
from Function import Function
from Workflow import Workflow
from Switch import Switch
import parser

objectMap = parser.objectMap
dispatch_pool = []
choices = dict()

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = f'http://{username}:{password}@127.0.0.1:5984/'
db_name = 'action_results'
db_server = couchdb.Server(couchdb_url)
db = db_server[db_name]
controller_url = 'http://0.0.0.0:18001/'

# For example, get the value of $.rand.Output.RandomNumber    
def parseOutput(expr, request_id):
    expr = expr.split('.')
    assert(len(expr) == 4 and expr[0] == '$' and expr[2] == 'Output')
    name = expr[1]
    key = expr[3]
    obj = objectMap[name]
    while type(obj) is not Function:
        if type(obj) is Workflow:
            obj = obj.end
        else:
            obj = choices[request_id][obj]
    result = db[obj.name + '_' + request_id]['result'][key]
    return result

# Check whether an exepression is true or not.
# For example, $.rand.Output.RandomNumber < 5    
symbols = ['<=', '>=', '==', '<', '>']
def parseExpr(expr, request_id):
    for s in symbols:
        if s in expr:
            left, right = expr.split(s)
            left = left.strip()
            right = right.strip()
            left_number = parseOutput(left, request_id) if '$' in left else int(left)
            right_number = parseOutput(right, request_id) if '$' in right else int(right)
            assert((type(left_number) is int) and (type(right_number) is int))
            if s == '<=':
                return left_number <= right_number
            elif s == '>=':
                return left_number >= right_number
            elif s == '==':
                return left_number == right_number
            elif s == '<':
                return left_number < right_number
            elif s == '>':
                return left_number > right_number

def run(obj, request_id):
    # print('run:', obj.name, request_id)
    if type(obj) is Function:
        runFunction(obj, request_id)
    elif type(obj) is Switch:
        runSwitch(obj, request_id)
    elif type(obj) is Workflow:
        runWorkflow(obj, request_id)

def runWorkflow(obj, request_id):
    run(obj.start, request_id)

def runSwitch(obj, request_id):
    for (choice, go) in obj.choices.items():
        if choice == 'default':
            choice[request_id][obj] = go
            run(go, request_id)
        elif parseExpr(choice, request_id):
            choice[request_id][obj] = go
            run(go, request_id)
            break

def runFunction(obj, request_id):
    # print('runFunc:', obj.name)
    gevent.joinall([gevent.spawn(runFunction_gevent, obj, request_id)])

def isEnd(obj):
    father = obj.father
    return type(father) is Switch or (type(father) is Workflow and father.end == obj)

def runFunction_gevent(obj, request_id):
    # print('runGevent:', obj.name)
    name = obj.name
    parameters = {}
    if obj.parameters != None:
        parameters = obj.parameters.copy()
        for (k, v) in parameters.items():
            if type(v) is str and '$' in v:
                parameters[k] = parseOutput(v, request_id)
        
    url = controller_url + 'run/' + obj.source
    send_id = name + '_' + request_id
    while True:
        try:
            # print('send_id:', send_id)
            res = requests.post(url, json = {"request_id": send_id, "data": parameters})    
            if res.text == 'OK':
                break
        except Exception:
            time.sleep(0.01)  
    
    while obj.father != None and isEnd(obj):
        obj = obj.father
    if obj.father == None: 
        result = db[name + '_' + request_id]['result']
        print('Request #{} execution complete: {}'.format(request_id, json.dumps(result)))
        if request_id in choices:
            choices.pop(request_id)
        return

    # Trigger new workflow / switch / function.
    for nxt in obj.next:
        prev_all_satisified = True
        for i in range(len(nxt.prev)):
            if nxt.prev[i] == obj:
                nxt.prev_set[i].add(request_id)
            elif request_id not in nxt.prev_set[i]:
                prev_all_satisified = False
        if prev_all_satisified:
            for i in range(len(nxt.prev)):
                nxt.prev_set[i].remove(request_id)
            run(nxt, request_id)

proxy = Flask(__name__)

@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    # print('id:', inp['request_id'])
    run(parser.mainObject, inp['request_id'])
    return ('OK', 200)

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 18000), proxy)
    server.serve_forever()

# total = 1
# for request_id in range(total):
#    gevent.sleep(1)
#    run(parser.mainObject, request_id)

# print(dispatch_pool)
# gevent.joinall(dispatch_pool)
