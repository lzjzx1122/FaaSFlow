from gevent import monkey

monkey.patch_all()
import uuid
import requests
import getopt
import sys
sys.path.append('..')
sys.path.append('../../../config')
from repository import Repository
import config
import pandas as pd
import time
import find_critical_path

repo = Repository()
CRIT_FUNCS = {'wordcount': ['start', 'count', 'merge'], 
              'illgal_recognizer': ["mosaic","translate","violence","virtual2","extract","word_censor","virtual1","upload"],
              'fileprocessing': ["conversion","upload","start"],
              'video': ["virtual1","split","merge","transcode","upload"]}
TEST_PER_WORKFLOW = 3 * 60

def run_workflow(workflow_name, request_id):
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    rep = requests.post(url, json=data)
    return rep.json()['latency']

def get_crit_latency(workflow_name, request_id):
    critical_path_functions = []
    if workflow_name in CRIT_FUNCS:
        critical_path_functions = CRIT_FUNCS[workflow_name]
    else:
        critical_path_functions = find_critical_path.analyze(workflow_name, request_id)
    crit_latency = 0
    docs = repo.get_latencies(request_id, 'all')
    mx = {}
    for doc in docs:
        if doc['function_name'] not in critical_path_functions:
            continue
        function_name = doc['function_name']
        if function_name not in mx:
            mx[function_name] = doc['time']
        else:
            mx[function_name] = max(mx[function_name], doc['time'])
    for k, v in mx.items():
        crit_latency += v
    return crit_latency

def analyze_workflow(workflow_name):
    print(f'----analyzing {workflow_name}----')
    repo.clear_couchdb_results()
    repo.clear_couchdb_workflow_latency()
    total = 0
    schedule_total = 0
    start = time.time()
    while time.time() - start <= TEST_PER_WORKFLOW and total <= 102:
        total += 1
        id = str(uuid.uuid4())
        print('----firing workflow----', id)
        e2e_latency = run_workflow(workflow_name, id)
        if total > 2:
            crit_latency = get_crit_latency(workflow_name, id)
            schedule_total += e2e_latency - crit_latency
            print('schedule_overhead: ', e2e_latency - crit_latency)
    scheduling_overhead = schedule_total / (total - 2)
    print(f'{workflow_name} schedule_overhead: ', scheduling_overhead)
    return scheduling_overhead

def analyze(mode):
    workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    # workflow_pool = ['illgal_recognizer', 'video', 'fileprocessing', 'wordcount']
    # workflow_pool = ['video']
    schedule_overhead = []
    for workflow in workflow_pool:
        schedule_overhead.append(analyze_workflow(workflow))
    df = pd.DataFrame({'workflow': workflow_pool, 'schedule_overhead': schedule_overhead})
    df.to_csv(mode + '.csv')

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],'',['controlmode='])
    for name, value in opts:
        if name == '--controlmode':
            mode = value
    analyze(mode)