import gevent
from gevent import monkey; monkey.patch_all()
import couchdb
import uuid
import requests
from repository import Repository
import time
import prepare_basic_input

repo = Repository()

def trigger_function(request_id, function_name):
    print('----triggering function ' + function_name + '----')
    info = repo.get_function_info(function_name, 'function_info')
    url = 'http://{}/request'.format(info['ip'])
    data = {
        'request_id': request_id,
        'workflow_name': 'test',
        'function_name': function_name,
        'no_parent_execution': True
    }
    requests.post(url, json=data)

def run_workflow(request_id):
    start_functions = repo.get_start_functions()
    jobs = []
    for n in start_functions:
        jobs.append(gevent.spawn(trigger_function, request_id, n))
    gevent.joinall(jobs)
    print('----ending----')

def analyze_overall_workflow():
    repo.reset_all_mem(clear_function_data=True)
    ids = [str(uuid.uuid4()) for i in range(12)]
    jobs = []
    for i in range(12):
        id = ids[i]
        print('----preparing basic input for request ', id, '----')
        jobs.append(gevent.spawn(prepare_basic_input.prepare_basic_input, id))
    gevent.joinall(jobs)
    e_total = 0
    n_total = 0
    overall_total = 0
    cnt = 0
    for id in ids:
        overall_start = time.time()
        run_workflow(id)
        overall_end = time.time()
        edge_time, node_time = repo.analyze_each_function(id)
        e = sum(edge_time.values())
        n = sum(node_time.values())
        print('----request ', id, ' finished, overall time: ', overall_end - overall_start, ' edge time: ', e, ' node time: ', n, '----')
        if cnt > 1:
            e_total += e
            n_total += n
            overall_total += overall_end - overall_start
        cnt = cnt + 1
    print('----overall time: ', overall_total / 10, ' edge_time: ', e_total / 10, ' node_time: ', n_total / 10, '----')
analyze_overall_workflow()

# edge_time, node_time = analyze_each_function('ac')
# print('edge_time', edge_time)
# print('node_time', node_time)