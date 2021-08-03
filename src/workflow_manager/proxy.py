import json
from typing import Dict
from gevent import monkey
monkey.patch_all()

import sys
from manager import WorkflowManager
from flask import Flask, request
app = Flask(__name__)

class Dispatcher:
    def __init__(self, mode: str, info_addrs: Dict[str, str]) -> None:
        self.managers = {name: WorkflowManager(sys.argv[1] + ':' + sys.argv[2], name, mode, addr) for name, addr in info_addrs.items()}
    
    def get_state(self, workflow_name: str, request_id: str) -> WorkflowManager:
        return self.managers[workflow_name].get_state(request_id)

    def trigger_function(self, workflow_name, state, function_name, no_parent_execution):
        self.managers[workflow_name].trigger_function(state, function_name, no_parent_execution)
    
    def clear_mem(self, workflow_name, request_id):
        self.managers[workflow_name].clear_mem(request_id)
    
    def clear_db(self, workflow_name, request_id):
        self.managers[workflow_name].clear_db(request_id)
    
    def del_state(self, workflow_name, request_id, master):
        self.managers[workflow_name].del_state(request_id, master)

dispatcher = Dispatcher(mode='raw', info_addrs={'genome': '../../benchmark/generator/genome', 'epigenomics': '../../benchmark/generator/epigenomics'})

# a new request from outside
# the previous function was done
@app.route('/request', methods = ['POST'])
def req():
    data = request.get_json(force=True, silent=True)
    request_id = data['request_id']
    workflow_name = data['workflow_name']
    function_name = data['function_name']
    no_parent_execution = data['no_parent_execution']
    # get the corresponding workflow state and trigger the function
    state = dispatcher.get_state(workflow_name, request_id)
    dispatcher.trigger_function(workflow_name, state, function_name, no_parent_execution)
    return json.dumps({'status': 'ok'})

@app.route('/clear', methods = ['POST'])
def clear():
    data = request.get_json(force=True, silent=True)
    workflow_name = data['workflow_name']
    request_id = data['request_id']
    master = False
    if 'master' in data:
        master = True
        dispatcher.clear_mem(workflow_name, request_id) # must clear memory after each run 
                                      # TODO: clear results in localized redis in each node
        dispatcher.clear_db(workflow_name, request_id) # optional: clear results in center db
    dispatcher.del_state(workflow_name, request_id, master) # and remove state for every node
    return json.dumps({'status': 'ok'})

from gevent.pywsgi import WSGIServer
import logging
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()
