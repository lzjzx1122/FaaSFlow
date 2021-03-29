import zipfile
import shutil
import os
import time
import re
import base64
from flask import Flask, request
from gevent.pywsgi import WSGIServer

default_file = 'main.py'

class functionRunner:
    def __init__(self):
        self.code = None
        self.function = None
        self.function_context = None

    def init(self, inp):
        # update function status
        function = inp['function']
        self.function = function

        os.chdir("/proxy")

        # compile the python file first
        filename = os.path.join("/proxy", default_file)
        with open(filename, 'r') as f:
            code = compile(f.read(), filename, mode='exec')

        self.function_context = {}
        exec(code, self.function_context)

        return True

    def run(self, inp):
        # insert the input to function's context
        self.function_context['data'] = inp

        # run the function
        out = eval('main(data)', self.function_context)
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
    runner.init(inp)

    proxy.status = 'ok'
    return ('OK', 200)

@proxy.route('/run', methods=['POST'])
def run():
    proxy.status = 'run'

    inp = request.get_json(force=True, silent=True)
    # record the execution time
    start = time.time()
    out = runner.run(inp)
    end = time.time()

    data = {
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        "result": out
    }

    proxy.status = 'ok'
    return data

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
