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
couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
db_server = couchdb.Server(couchdb_url)
latency_db = db_server['workflow_latency']

class Runner:
    def __init__(self):
        self.code = None
        self.workflow = None
        self.function = None
        self.ctx = {}

    def init(self, workflow, function):
        print('init...')

        # update function status
        self.workflow = workflow
        self.function = function

        os.chdir(work_dir)

        # compile first
        filename = os.path.join(work_dir, default_file)
        with open(filename, 'r') as f:
            self.code = compile(f.read(), filename, mode='exec')

        print('init finished...')

    def run(self, request_id, runtime, input, output, to, keys):
        # run the function
        self.ctx['workflow_name'] = self.workflow
        self.ctx['function_name'] = self.function
        self.ctx['request_id'] = request_id
        self.ctx['runtime'] = runtime
        self.ctx['input'] = input
        self.ctx['output'] = output
        self.ctx['to'] = to
        self.ctx['keys'] = keys

        print('running... context: ', self.ctx)
        exec(self.code, self.ctx)
        start = time.time()
        out = eval('main()', self.ctx)
        end = time.time()
        latency_db.save({'request_id': request_id, 'function_name': self.function, 'phase': 'edge+node', 'time': end - start})
        return out


proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
runner = Runner()


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
    runner.init(inp['workflow'], inp['function'])

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
    to = inp['to']
    keys = inp['keys']

    # record the execution time
    start = time.time()
    runner.run(request_id, runtime, input, output, to, keys)
    end = time.time()

    res = {
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        "inp": inp
    }

    proxy.status = 'ok'
    return res


if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
