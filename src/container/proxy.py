import zipfile
import shutil
import os
import time
import re
import base64
import couchdb
import json
import threading
from flask import Flask, request
from gevent.pywsgi import WSGIServer

default_file = 'main.py'
work_dir = '/proxy'
  
class functionRunner:
    def __init__(self):
        self.code = None
        self.function = None
        self.ctx = None
        
    def init(self, function):
        # update function status
        self.function = function

        os.chdir(work_dir)

        # compile the python file first
        filename = os.path.join(work_dir, default_file)
        with open(filename, 'r') as f:
            code = compile(f.read(), filename, mode='exec')

        self.ctx = {}
        exec(code, self.ctx)

        return True

    def run(self, request_id, runtime, input, output, foreach_id):
        # run the function
        self.ctx['function_name'] = self.function
        self.ctx['request_id'] = request_id
        self.ctx['runtime'] = runtime
        self.ctx['input'] = input
        self.ctx['output'] = output
        self.ctx['foreach_id'] = foreach_id
        out = eval('main(function_name, request_id, runtime, input, output, foreach_id)', self.ctx)
        return out

proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
runner = functionRunner()

@proxy.route('/status', methods=['GET'])
def status():
    res = {}
    res['status'] = proxy.status
    res['workdir'] = os.getcwd()
    if runner.function:
        res['function'] = runner.function
    return res

@proxy.route('/init', methods=['POST'])
def init():
    proxy.status = 'init'

    inp = request.get_json(force=True, silent=True)
    runner.init(inp['function'])
    
    proxy.status = 'ok'
    return ('OK', 200)

@proxy.route('/run', methods=['POST'])
def run():
    proxy.status = 'run'

    inp = request.get_json(force=True, silent=True)
    request_id = inp['request_id']
    runtime = inp['runtime']
    input = inp['input']
    output = inp['output']
    foreach_id = None
    if 'foreach_id' in inp:
        foreach_id = inp

    # record the execution time
    start = time.time()
    runner.run(request_id, runtime, input, output, foreach_id)
    end = time.time()

    res = {
        "start_time": start,
        "end_time": end,
        "duration": end - start
    }
    
    proxy.status = 'ok'
    return res

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
