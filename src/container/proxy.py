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
        couchdb_url = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
        db_server = couchdb.Server(couchdb_url)
        self.db = db_server['results']
        self.fetch_dict = {}
        self.put_dict = {}
    
    def init(self, function):
        self.function = function

    def fetch_from_mem(self, path, key):
        with open(path, "r") as f:
            json_file = json.load(f)
            self.fetch_dict[key] = json_file['value']

    def fetch_from_db(self, doc, key):
        self.fetch_dict[key] = self.db[doc]['value']

    def fetch(self, request_id, input):
        self.fetch_dict = {}
        threads = []
        for (k, v) in input.items():
            if v['type'] == 'DB': #DB
                doc = request_id + "_" + k
                thread_ = threading.Thread(target=self.fetch_from_db, args=(doc, k,))
                threads.append(thread_)
            else: # MEM
                path = os.path.join(result_dir, request_id + "_" + k + ".json")
                thread_ = threading.Thread(target=self.fetch_from_mem, args=(path, k,))
                threads.append(thread_)
        for thread_ in threads:
            thread_.start()
        for thread_ in threads:
            thread_.join()
        return self.fetch_dict

    def put_to_mem(self, path, key):
        with open(path, "w") as f:
            json_file = {"key": key, "value": self.put_dict[key]}
            json.dump(json_file, f)
    
    def put_to_db(self, doc, key):
        self.db[doc] = {"key": key, "value":  self.put_dict[key]}

    def put(self, request_id, output, output_res):
        self.put_dict = output_res 
        threads = []
        for (k, v) in output_res.items():
            if 'DB' in output[k]['type']:
                doc = request_id + "_" + k
                thread_ = threading.Thread(target=self.put_to_db, args=(doc, k,))
                threads.append(thread_)
            if 'MEM' in output[k]['type']:
                path = os.path.join(result_dir, request_id + "_" + k + ".json")
                thread_ = threading.Thread(target=self.put_to_mem, args=(path, k,))
                threads.append(thread_)
        for thread_ in threads:
            thread_.start()
        for thread_ in threads:
            thread_.join()

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
    input_res = store.fetch(request_id, input)

    # record the execution time
    start = time.time()
    output_res = runner.run(runtime, input_res, output)
    end = time.time()

    store.put(request_id, output, output_res)
    
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
