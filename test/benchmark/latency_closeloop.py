import gevent
from gevent import monkey; monkey.patch_all()
import couchdb
import uuid
import requests
from repository import Repository
import time

repo = Repository()
f = open('latency_results.txt', 'w')

def trigger_function(workflow_name, request_id, function_name):
    # print('----triggering function ' + function_name + '----')
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
    repo.allocate_db(request_id)
    start_functions = repo.get_start_functions(workflow_name + '_workflow_metadata')
    start = time.time()
    jobs = []
    for n in start_functions:
        jobs.append(gevent.spawn(trigger_function, workflow_name, request_id, n))
    gevent.joinall(jobs)
    end = time.time()
    master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
    clear_url = 'http://{}/clear'.format(master_addr)
    requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})
    return end - start

def analyze_workflow(workflow_name):
    # repo.reset_all_mem(clear_function_data=True)
    top = 5
    ids = [str(uuid.uuid4()) for i in range(top)]
    overall_total = 0
    cnt = 0
    # e_total = 0
    # n_total = 0
    # node_dict = {'upload': 0, 'split': 0, 'transcode': 0, 'merge': 0}
    for id in ids:
        print('----firing workflow ', id)
        overall_latency = run_workflow(workflow_name, id)
        # if workflow_name == 'video':
        # time.sleep(3)
        # edge_time, node_time = repo.analyze_each_function(id)
            # for name in node_time:
            #     node_dict[name] += node_time[name]
        # e = sum(edge_time.values())
        # n = sum(node_time.values())
        print('----request ', id, ' finished, overall time: ', overall_latency)
        # if cnt > 0:
            # e_total += e
            # n_total += n
        overall_total += overall_latency
        # cnt = cnt + 1
    print('coordination latency', (overall_total - repo.get_crit_latency()) / top)
    # print('----workflow_name: ', workflow_name, ' overall time: ', overall_total / (top - 2), ' edge time: ', e_total / (top - 2), ' node_time: ', n_total / (top - 2), '----')
    # print('!!!!workflow_name: ', workflow_name, ' overall time: ', overall_total / (top - 1))
    # f.write(workflow_name + ': ' + str(overall_total / (top - 1)) + '\n')

def analyze():
    repo.reset_all_mem(clear_function_data=True)
    # workflow_pool = ['genome', 'soykb', 'epigenomics', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    workflow_pool = ['genome']
    jobs = []
    cnt = 0
    for workflow_name in workflow_pool:
        jobs.append(gevent.spawn_later(cnt * 5, analyze_workflow, workflow_name))
        cnt = cnt + 1
    gevent.joinall(jobs)

analyze()
# edge_time, node_time = analyze_each_function('ac')
# print('edge_time', edge_time)
# print('node_time', node_time)