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

repo = Repository()
TEST_PER_WORKFLOW = 2 * 60

def run_workflow(workflow_name, request_id):
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    rep = requests.post(url, json=data)
    return rep.json()['latency']

def get_data_overhead(request_id):
    data_overhead = 0
    docs = repo.get_latencies(request_id, 'edge')
    for doc in docs:
        data_overhead += doc['time']
    return data_overhead

def analyze_workflow(workflow_name):
    print(f'----analyzing {workflow_name}----')
    repo.clear_couchdb_results()
    repo.clear_couchdb_workflow_latency()
    total = 0
    start = time.time()
    data_total = 0
    while time.time() - start <= TEST_PER_WORKFLOW and total <= 102:
        total += 1
        id = str(uuid.uuid4())
        print('----firing workflow----', id)
        e2e_latency = run_workflow(workflow_name, id)
        if total > 2:
            data_overhead = get_data_overhead(id)
            data_total += data_overhead
            print('e2e latency: ', e2e_latency)
            print('data_overhead: ', data_overhead)
    data_overhead = data_total / (total - 2)
    print(f'{workflow_name} data_overhead: ', data_overhead)
    return data_overhead

def analyze(mode):
    # workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    # workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb']
    workflow_pool = ['genome']
    data_overhead = []
    for workflow in workflow_pool:
        data_overhead.append(analyze_workflow(workflow))
    df = pd.DataFrame({'workflow': workflow_pool, 'data_overhead': data_overhead})
    df.to_csv(mode + '2.csv')

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],'',['datamode='])
    for name, value in opts:
        if name == '--datamode':
            mode = value
    analyze(mode)