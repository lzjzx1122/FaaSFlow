import json
import gevent
from gevent import monkey
monkey.patch_all()
import sys
from flask import Flask, request
from repository import Repository
import requests
import time
import config

app = Flask(__name__)
repo = Repository()

def trigger_function(workflow_name, request_id, function_name):
    info = repo.get_function_info(function_name, workflow_name + '_function_info')
    ip = ''
    if config.CONTROL_MODE == 'WorkerSP':
        ip = info['ip']
    elif config.CONTROL_MODE == 'MasterSP':
        ip = config.MASTER_HOST
    url = 'http://{}/request'.format(ip)
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
    start = time.time()
    jobs = []
    for n in start_functions:
        jobs.append(gevent.spawn(trigger_function, workflow_name, request_id, n))
    gevent.joinall(jobs)
    end = time.time()

    # clear memory and other stuff
    if config.CLEAR_DB_AND_MEM:
        master_addr  = ''
        if config.CONTROL_MODE == 'WorkerSP':
            master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
        elif config.CONTROL_MODE == 'MasterSP':
            master_addr = config.MASTER_HOST
        clear_url = 'http://{}/clear'.format(master_addr)
        requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})
    
    return end - start

@app.route('/run', methods = ['POST'])
def run():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    request_id = data['request_id']
    logging.info('processing request ' + request_id + '...')
    repo.log_status(workflow, request_id, 'EXECUTE')
    latency = run_workflow(workflow, request_id)
    repo.log_status(workflow, request_id, 'FINISH')
    return json.dumps({'status': 'ok', 'latency': latency})

@app.route('/clear_conainer', methods = ['GET'])
def clear_container():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    addrs = repo.get_all_addrs(workflow + '_workflow_metadata')
    jobs = []
    for addr in addrs:
        clear_url = f'http://{addr}/clear_container'
        jobs.append(gevent.spawn(requests.get, clear_url))
    gevent.joinall(jobs)
    return json.dumps({'status': 'ok'})

from gevent.pywsgi import WSGIServer
import logging
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level='INFO')
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()