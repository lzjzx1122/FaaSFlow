import zipfile
import shutil
import os
import time
import re
import base64
from flask import Flask, request
from gevent.pywsgi import WSGIServer

action_path = '/proxy/actions/'
exec_path = '/proxy/exec/'
default_file = 'main.py'

class ActionRunner:
    def __init__(self):
        self.code = None
        self.action = None
        self.action_context = None
        
        self.action_list = []
        for filename in os.listdir(action_path):
            m = re.fullmatch(r'action_(.*)\.zip', filename)
            if m is not None:
                self.action_list.append(m.group(1))

    def init(self, inp):
        action = inp['action']
        pwd = inp['pwd']

        # update action status
        self.action = action

        # remove previous files in exec dir
        shutil.rmtree(exec_path)
        os.mkdir(exec_path)
        os.chdir(exec_path)

        # extract the zipfile
        zipname = action_path + 'action_' + action + '.zip'
        with zipfile.ZipFile(zipname) as f:
            f.extractall(exec_path, pwd=bytes(pwd, 'ascii'))

        # compile the python file first
        filename = exec_path + default_file
        with open(filename, 'r') as f:
            code = compile(f.read(), filename, mode='exec')

        self.action_context = {}
        exec(code, self.action_context)

        return True

    def run(self, inp):
        # insert the input to action's context
        self.action_context['data'] = inp

        # run the action
        out = eval('main(data)', self.action_context)
        return out

    def inject(self, name, file):
        pass

proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
runner = ActionRunner()

@proxy.route('/status', methods=['GET'])
def status():
    res = {}
    res['status'] = proxy.status
    res['actions'] = runner.action_list
    if runner.action:
        res['cur_action'] = runner.action
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

@proxy.route('/inject', methods=['POST'])
def inject():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action']
    zip_encoded = inp['zipfile']
    zip_path = os.path.join(action_path, f'action_{action_name}.zip')
    with open(zip_path, 'wb') as f:
        f.write(base64.standard_b64decode(zip_encoded))
    runner.action_list.append(action_name)
    return ('OK', 200)

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
