import couchdb
import uuid
import requests
from repository import Repository
import gevent
import time
import prepare_basic_input

couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
db_server = couchdb.Server(couchdb_url)
db = db_server['workflow_latency']
repo = Repository()

def analyze_each_function(request_id):
    edge_time = {}
    node_time = {}
    transcode_cnt = 0
    for doc in db:
        if db[doc]['request_id'] != request_id:
            continue
        function_name = db[doc]['function_name']
        phase = db[doc]['phase']
        latency = db[doc]['time']
        if phase == 'edge+node':
            node_time.setdefault(function_name, 0)
            node_time[function_name] += latency
        else:
            edge_time.setdefault(function_name, 0)
            edge_time[function_name] += latency
            # if function_name == 'transcode':
            #     transcode_cnt = transcode_cnt+1
    for name in node_time:
        node_time[name] -= edge_time[name]
        # if name == 'transcode':
        #     node_time[name] /= transcode_cnt
        #     edge_time[name] /= transcode_cnt
    return edge_time, node_time

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

def analyze_overall_workflow():
    db_server.delete('results')
    db_server.delete('workflow_latency')
    db_server.create('results')
    db_server.create('workflow_latency')
    repo.mem_clearall()
    ids = [str(uuid.uuid4()) for i in range(12)]
    for i in range(12):
        id = ids[i]
        print('----preparing basic input for request ', id, '----')
        prepare_basic_input.main(id, 'sample.md')
    e_total = 0
    n_total = 0
    overall_total = 0
    cnt = 0
    for id in ids:
        overall_start = time.time()
        run_workflow(id)
        overall_end = time.time()
        edge_time, node_time = analyze_each_function(id)
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