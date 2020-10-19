import threading
import json
import os
import sys
import time
from ServerlessBase import ServerlessBase
from Function import Function
from Workflow import Workflow
from Switch import Switch
import parse

path = sys.argv[1]
db_path = path + 'db/'
if not os.path.exists(db_path):
    os.mkdir(db_path)

thread_pool = []
thread_pool_lock = threading.Lock()
prev_lock = threading.Lock()

# Get the value of an expression.    
# For example, get the value of $.rand.Output.RandomNumber    
def getOutput(expr, request_id):
    expr = expr.split('.')
    assert(len(expr) == 4 and expr[0] == '$' and expr[2] == 'Output')
    filename = db_path + expr[1] + '_' + str(request_id) + '.json'
    json_data = json.load(open(filename))
    output = json_data[expr[3]]
    # assert(type(output) is int)
    return output

# Check whether an exepression is true or not.
# For example, $.rand.Output.RandomNumber < 5    
symbols = ['<=', '>=', '==', '<', '>']
def checkExpr(expr, request_id):
    for s in symbols:
        if s in expr:
            left, right = expr.split(s)
            left = left.strip()
            right = right.strip()
            left_number = getOutput(left, request_id) if '$' in left else int(left)
            right_number = getOutput(right, request_id) if '$' in right else int(right)
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


def executeFunction_thread(obj, request_id):
    name = obj.name
    parameters = ''
    if obj.parameters != None:
        parameters = obj.parameters.copy()
        for (k, v) in parameters.items():
            if type(v) is str and '$' in v:
                parameters[k] = getOutput(v, request_id)
        parameters = json.dumps(parameters)

    # Create a new process.
    # For example, python3 sqrt.py '{"x": 4}' > sqrt_0.json
    filename = db_path + name + '_' + str(request_id) + '.json'
    execute_str = 'python3 ' + path + obj.source + ' \'' + parameters + '\'' + ' > ' + filename
    os.system(execute_str)
    
    while obj.father != None:
        cp_filename = db_path + obj.father.name + '_' + str(request_id) + '.json'
        if type(obj.father) is Switch:
            os.system('cp ' + filename + ' ' + cp_filename)
            obj = obj.father
        elif type(obj.father) is Workflow and obj.father.end == obj:
            os.system('cp ' + filename + ' ' + cp_filename)
            obj = obj.father
        else:
            break

    # Workflow execution complete.
    if obj.father == None: 
        filename = db_path + name + '_' + str(request_id) + '.json'
        result = json.load(open(filename))
        print('Request #{} execution complete: {}'.format(request_id, json.dumps(result)))

    # Trigger new workflow / switch / function.
    prev_lock.acquire()
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
            execute(nxt, request_id)
    prev_lock.release()


def executeFunction(obj, request_id):
    t = threading.Thread(target=executeFunction_thread, args=(obj, request_id))
    thread_pool_lock.acquire()
    thread_pool.append(t)
    thread_pool_lock.release()
    t.start()


def executeSwitch(obj, request_id):
    for (choice, go) in obj.choices.items():
        if choice == 'default':
            execute(go, request_id)
        elif checkExpr(choice, request_id):
                execute(go, request_id)
                break


def executeWorkflow(obj, request_id):
    execute(obj.start, request_id)


def execute(obj, request_id):
    if type(obj) is Function:
        executeFunction(obj, request_id)
    elif type(obj) is Switch:
        executeSwitch(obj, request_id)
    elif type(obj) is Workflow:
        executeWorkflow(obj, request_id)

total = 10
for request_id in range(total):
    time.sleep(0.1)
    execute(parse.mainObject, request_id)

for t in thread_pool:
    t.join()