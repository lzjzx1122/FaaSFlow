import json
import gevent
from gevent import monkey
monkey.patch_all()
import sys
from flask import Flask, request
from repository import Repository
import requests
import time

app = Flask(__name__)
repo = Repository()

def trigger_function(workflow_name, request_id, function_name):
    info = repo.get_function_info(function_name, workflow_name + '_function_info')
    url = 'http://{}/request'.format(info['ip'])
    data = {
        'request_id': request_id,
        'workflow_name': workflow_name,
        'function_name': function_name,
        'no_parent_execution': True
    }
    requests.post(url, json=data)

def run_workflow(workflow_name, request_id):
    repo.create_request_doc(request_id)

    # allocate works
    start_functions = repo.get_start_functions(workflow_name + '_workflow_metadata')
    jobs = []
    for n in start_functions:
        jobs.append(gevent.spawn(trigger_function, workflow_name, request_id, n))
    gevent.joinall(jobs)

    # clear memory and other stuff
    master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
    clear_url = 'http://{}/clear'.format(master_addr)
    requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})

@app.route('/run', methods = ['POST'])
def run():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    request_id = data['request_id']
    logging.info('processing request ' + request_id + '...')
    repo.log_status(workflow, request_id, 'EXECUTE')
    run_workflow(workflow, request_id)
    repo.log_status(workflow, request_id, 'FINISH')
    return json.dumps({'status': 'ok'})

@app.route('/dispatch', methods = ['GET'])
def dispatch():
    logging.info('dispatching work, stand by...')
    time.sleep(2)
    return json.dumps({'status': 'ok'})

from gevent.pywsgi import WSGIServer
import logging
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level='INFO')
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()