import threading
import json
import os
import sys
from ServerlessBase import ServerlessBase
from Function import Function
from Workflow import Workflow
from Switch import Switch
import parse

path = sys.argv[1]
create_lock = threading.Lock()
thread_pool = []


def trigger(node):
    t = threading.Thread(target=execute, args=(node,))
    thread_pool.append(t)
    t.start()

def executeFunction(obj):
    parameters = json.dumps(obj.parameters)
    os.system('python3 ' + path + obj.operation + ' \'' + parameters + '\'')
    for node in obj.next:
        create_lock.acquire()
        node.prev_finished += 1
        if node.prev_finished == len(node.prev):
            trigger(node)
        create_lock.release()

def executeSwitch(obj):
    create_lock.acquire()
    trigger(obj.choices['default'])
    create_lock.release()

def executeWorkflow(obj):
    create_lock.acquire()
    trigger(obj.start)
    create_lock.release()

def execute(obj):
    if type(obj) is Function:
        executeFunction(obj)
    elif type(obj) is Switch:
        executeSwitch(obj)
    else:
        executeWorkflow(obj)


trigger(parse.mainObject)

for t in thread_pool:
    t.join()

