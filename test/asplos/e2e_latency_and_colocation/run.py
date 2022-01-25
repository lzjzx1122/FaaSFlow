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
import gevent

repo = Repository()
TEST_PER_WORKFLOW = 2 * 60
TEST_CORUN = 2 * 60
TIMEOUT = 60
e2e_dict = {}

def run_workflow(workflow_name, request_id):
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    try:
        rep = requests.post(url, json=data, timeout=TIMEOUT)
        return rep.json()['latency']
    except Exception:
        print(f'{workflow_name} timeout')
        return 1000

def analyze_workflow(workflow_name, mode):
    global e2e_dict
    total = 0
    start = time.time()
    e2e_total = 0
    timeout = 0
    LIMIT = TEST_PER_WORKFLOW if mode == 'single' else TEST_CORUN
    while timeout < 5 and (total < 3 or time.time() - start <= LIMIT):
        total += 1
        id = str(uuid.uuid4())
        print(f'----firing workflow {workflow_name}----', id)
        e2e_latency = run_workflow(workflow_name, id)
        if total > 2:
            if e2e_latency > 100:
                total = total - 1
                timeout = timeout + 1
            else:
                e2e_total += e2e_latency
                print('e2e_latency: ', e2e_latency)
    if timeout >= 5:
        print(f'{workflow_name} e2e_latency: timeout')
        e2e_dict[workflow_name] = 'timeout'
    else:
        e2e_latency = e2e_total / (total - 2)
        print(f'{workflow_name} e2e_latency: ', e2e_latency)
        e2e_dict[workflow_name] = e2e_latency

def analyze(mode, datamode):
    global e2e_dict
    workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    # workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb']
    # workflow_pool = ['soykb']
    if mode == 'single':
        for workflow in workflow_pool:
            analyze_workflow(workflow, mode)
    elif mode == 'corun':
        jobs = []
        for i, workflow_name in enumerate(workflow_pool):
            jobs.append(gevent.spawn_later(i * 5, analyze_workflow, workflow_name, mode))
        gevent.joinall(jobs)
    print(e2e_dict)
    e2e_latencies = []
    for workflow in workflow_pool:
        e2e_latencies.append(e2e_dict[workflow])
    df = pd.DataFrame({'workflow': workflow_pool, 'e2e_latency': e2e_latencies})
    df.to_csv(f'{datamode}_{mode}.csv')

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],'',['mode=', 'datamode='])
    repo.clear_couchdb_results()
    repo.clear_couchdb_workflow_latency()
    for name, value in opts:
        if name == '--mode':
            mode = value
        elif name == '--datamode':
            datamode = value
    analyze(mode, datamode)
