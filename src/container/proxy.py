import zipfile
import shutil
import os
import time
import re
import base64
import couchdb
import json
from flask import Flask, request
from gevent.pywsgi import WSGIServer

default_file = 'main.py'
work_dir = '/exec'
result_dir = "/results"
  
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

    def run(self, runtime, input, output):
        # run the function
        self.ctx['runtime'] = runtime
        self.ctx['input'] = input
        self.ctx['output'] = output
        out = eval('main(runtime, input, output)', self.ctx)
        return out


class Store:
    def __init__(self):
        username = 'openwhisk'
        password = 'openwhisk'
        hostname = '10.2.64.8'
        couchdb_url = f'http://{username}:{password}@{hostname}:5984/'
        db_server = couchdb.Server(couchdb_url)
        self.db = db_server['results']
    
    def init(self, function):
        self.function = function

    def fetch(self, input):
        input_res = {}
        for (k, v) in input.items():
            if v['type'] == 'DB':
                doc = v['value']
                input_res[k] = self.db[doc]
            else: # MEM
                path = v['value']
                with open(os.path.join(result_dir, path), "r") as f:
                    json_file = json.load(f)
                    input_res[k] = json_file['value']
        return input_res
        
    def put(self, request_id, output, output_res):
        for (k, v) in output_res.items():
            if output[k]['type'] == 'DB':
                doc = request_id + "_" + self.function + "_" + k
                self.db[doc] = {"key": k, "value": v}
                output[k]['value'] = doc
            else: # MEM
                path = request_id + "_" + self.function + "_" + k + ".json"
                json_file = {"key": k, "value": v}
                with open(os.path.join(result_dir, path), "w") as f:
                    json.dump(json_file, f)
                output[k]['value'] = path
        return output

proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
runner = functionRunner()
store = Store()

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
    store.init(inp['function'])

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
    input_res = store.fetch(input)

    # record the execution time
    start = time.time()
    output_res = runner.run(runtime, input_res, output)
    end = time.time()

    output = store.put(request_id, output, output_res)
    
    res = {
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        "output": output
    }
    
    proxy.status = 'ok'
    return res

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
