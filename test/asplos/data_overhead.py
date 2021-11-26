from gevent import monkey
monkey.patch_all()
import uuid
from repository import Repository
import config
import requests

repo = Repository()
f = open('./data/data_overhead.txt', 'w')

def run_workflow(workflow_name, request_id):
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    rep = requests.post(url, json=data)
    return rep.json()['latency']

def get_data_overhead(request_id):
    db = repo.get_latencies()
    data_overhead = 0
    for _id in db:
        if db[_id]['request_id'] != request_id or db[_id]['phase'] != 'edge':
            continue
        data_overhead += db[_id]['time']
    return data_overhead

def analyze_workflow(workflow_name):
    repo.clear_couchdb_results()
    repo.clear_redis_cache()
    repo.clear_couchdb_workflow_latency()
    total = 5
    ids = [str(uuid.uuid4()) for i in range(total)]
    e_total = 0
    for i, id in enumerate(ids):
        print('----firing workflow ', id)
        run_workflow(workflow_name, id)
        if i >= 2:
            e_latency = get_data_overhead(id)
            print('data overhead: ', e_latency)
            e_total += e_latency
    e_total /= total - 2
    f.write(workflow_name + ': ' + str(e_total) + '\n')
    f.flush()

def analyze():
    # workflow_pool = ['video', 'illgal_recognizer', 'fileprocessing', 'wordcount', 'cycles', 'epigenomics', 'genome', 'soykb']
    workflow_pool = ['video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    # workflow_pool = ['illgal_recognizer']
    for workflow in workflow_pool:
        analyze_workflow(workflow)

if __name__ == '__main__':
    analyze()