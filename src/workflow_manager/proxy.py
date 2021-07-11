from gevent import monkey
monkey.patch_all()

import sys
from manager import WorkflowManager
from flask import Flask, request
app = Flask(__name__)
manager = WorkflowManager(sys.argv[1], 'test', 'optimized') # TODO: support multi workflow

# a new request from outside
# the previous function was done
@app.route('/request')
def req():
    data = request.get_json(force=True, silent=True)
    request_id = data['request_id']
    workflow_name = data['workflow_name']
    function_name = data['function_name']

    # get the corresponding workflow state and trigger the function
    state = manager.get_state(request_id)
    manager.trigger_function_local(state, function_name)

    return {'status': 'ok'}

from gevent.pywsgi import WSGIServer
if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5001), app)
    server.serve_forever()
