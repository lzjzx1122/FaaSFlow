from gevent import monkey

from test.benchmark.throughput import run
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
current_workflow = ''
RPM = 0
BANDWIDTH = 0 

def run_workflow(workflow_name, request_id):
    global latencies, current_workflow
    gevent.spawn_later(60 / RPM, run_workflow, workflow_name, str(uuid.uuid4()))
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    rep = requests.post(url, json=data, timeout=100)
    latencies.append(rep.json()['latency'])

def analyze(workflow_name):
    

if __name__ == '__main__':
    global running, RPM, BANDWIDTH
    opts, args = getopt.getopt(sys.argv[1:],'',['rpm=', 'bandwidth='])
    for name, value in opts:
        if name == '--rpm':
            RPM = int(value)
        elif name == '--bandwidth':
            BANDWIDTH = int(value)
    workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    for workflow in workflow_pool:
        running = True
        gevent.spawn_later(60 / RPM, run_workflow, workflow, str(uuid.uuid4()))
        analyze(workflow_name)
        gevent.sleep()