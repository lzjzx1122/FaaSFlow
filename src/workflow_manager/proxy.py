import json
from gevent import monkey
monkey.patch_all()

import sys
from manager import WorkflowManager
from flask import Flask, request
app = Flask(__name__)
manager = WorkflowManager(sys.argv[1] + ':' + sys.argv[2], 'test', 'optimized') # TODO: support multi workflow

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

from gevent.pywsgi import WSGIServer
if __name__ == '__main__':
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()
