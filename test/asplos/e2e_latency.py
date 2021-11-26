from gevent import monkey; monkey.patch_all()
import uuid
import requests
from repository import Repository
import config

repo = Repository()
f = open('./data/e2e_latency.txt', 'w')

def run_workflow(workflow_name, request_id):
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    rep = requests.post(url, json=data)
    return rep.json()['latency']

def analyze_workflow(workflow_name):
    repo.clear_couchdb_results()
    repo.clear_redis_cache()
    repo.clear_couchdb_workflow_latency()
    total = 5
    ids = [str(uuid.uuid4()) for i in range(total)]
    e2e_total = 0
    for i in range(total):
        id = ids[i]
        print('----firing workflow----', id)
        e2e_latency = run_workflow(workflow_name, id)
        if i >= 2:
            e2e_total += e2e_latency
            print('e2e_latency: ', e2e_latency)
    e2e_total /= total - 2
    f.write(workflow_name + ': ' + str(e2e_total) + '\n')
    f.flush()

def analyze():
    # workflow_pool = ['video', 'illgal_recognizer', 'fileprocessing', 'wordcount', 'cycles', 'epigenomics', 'genome', 'soykb']
    workflow_pool = ['video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    # workflow_pool = ['illgal_recognizer']
    for workflow in workflow_pool:
        analyze_workflow(workflow)

if __name__ == '__main__':
    analyze()