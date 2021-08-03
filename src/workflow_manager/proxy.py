import json
from gevent import monkey
monkey.patch_all()

import sys
from manager import WorkflowManager
from flask import Flask, request
app = Flask(__name__)
manager = WorkflowManager(sys.argv[1] + ':' + sys.argv[2], 'test', 'raw') # TODO: support multi workflow
# manager.show_state()

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
    state = manager.get_state(request_id)
    manager.trigger_function(state, function_name, no_parent_execution)
    return json.dumps({'status': 'ok'})

@app.route('/clear', methods = ['POST'])
def clear():
    data = request.get_json(force=True, silent=True)
    request_id = data['request_id']
    master = False
    if 'master' in data:
        master = True
        manager.clear_mem(request_id) # must clear memory after each run 
                                      # TODO: clear results in localized redis in each node
        manager.clear_db(request_id) # optional: clear results in center db
    manager.del_state(request_id, master) # and remove state for every node
    return json.dumps({'status': 'ok'})

from gevent.pywsgi import WSGIServer
if __name__ == '__main__':
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()
