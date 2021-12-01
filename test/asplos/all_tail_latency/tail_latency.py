from gevent import monkey
monkey.patch_all()
import uuid
import requests
import getopt
import sys
sys.path.append('..')
from repository import Repository
import config
import pandas as pd
import time
import gevent

repo = Repository()
latencies = []
ticket = 0
running = 0
timeout = 0
RPM = 8
BANDWIDTH = 0 
TEST_PER_WORKFLOW = 3 * 60

def run_workflow(workflow_name, request_id):
    print('----firing workflow----', request_id)
    global latencies, ticket, running, timeout
    ticket = ticket - 1
    running = running + 1
    if ticket > 0 and timeout < 3:
        gevent.spawn_later(60 / RPM, run_workflow, workflow_name, str(uuid.uuid4()))
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    try:
        rep = requests.post(url, json=data, timeout=60)
        e2e_latency = rep.json()['latency']
        latencies.append(e2e_latency)
        print('e2e latency: ', e2e_latency)
    except Exception:
        print(f'{workflow_name} timeout')
        timeout = timeout + 1
    running = running - 1

def analyze_workflow():
    global latencies, timeout
    if timeout >= 3:
        return 'timeout'
    if len(latencies) < 100:
        return latencies[-2]
    else:
        tail = int(len(latencies) / 100)
        return latencies[-tail]

def analyze(datamode):
    global RPM, BANDWIDTH, ticket, running, timeout
    workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    tail_latencies = []
    for workflow in workflow_pool:
        print(f'----analyzing {workflow}----')

        # prewarm to achieve stable throughput
        timeout = 0
        for _ in range(3):
            try:
                url = 'http://' + config.GATEWAY_ADDR + '/run'
                data = {'workflow':workflow, 'request_id': str(uuid.uuid4())}
                requests.post(url, json=data, timeout=60)
            except Exception:
                print(f'{workflow} timeout')
                timeout = timeout + 1
        if timeout == 3:
            tail_latencies.append('timeout')
            clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
            data = {'workflow': workflow}
            requests.get(clear_url)
            continue

        # tail latency analysis
        ticket = RPM * TEST_PER_WORKFLOW / 60
        running = 0
        timeout = 0
        gevent.spawn(run_workflow, workflow, str(uuid.uuid4()))
        gevent.sleep(5)
        while True:
            if running == 0 and timeout != 0: # timeout
                break
            if ticket == 0 and running == 0: # finished running
                break
            print(f'ticket: {ticket}, running: {running}, timeout: {timeout}')
            gevent.sleep(5)
        tail_latencies.append(analyze_workflow())
    df = pd.DataFrame({'workflow': workflow_pool, 'tail_latency': tail_latencies})
    df.to_csv(f'{datamode}_{RPM}rpm_{BANDWIDTH}mb.csv')

if __name__ == '__main__':
    repo.clear_couchdb_results()
    repo.clear_couchdb_workflow_latency()
    opts, args = getopt.getopt(sys.argv[1:],'',['rpm=', 'bandwidth=', 'datamode='])
    for name, value in opts:
        if name == '--rpm':
            RPM = int(value)
        elif name == '--bandwidth':
            BANDWIDTH = int(value)
        elif name == '--datamode':
            datamode = value
    analyze(datamode)
        