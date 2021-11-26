from gevent import monkey; monkey.patch_all()
import uuid
import requests
from repository import Repository
import config

repo = Repository()
f = open('./data/scheduling_overhead.txt', 'w')
CRIT_FUNCS = {'wordcount': ['start', 'count', 'merge'], 
              'illgal_recognizer': ["mosaic","translate","violence","virtual2","extract","word_censor","virtual1","upload"],
              'fileprocessing': ["conversion","upload","start"],
              'video': ["virtual1","split","merge","transcode","upload"]}

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
        critical_path_functions = repo.get_critical_path_functions(workflow_name)
    crit_latency = 0
    db = repo.get_latencies()
    mx = {}
    for _id in db:
        if db[_id]['request_id'] != request_id or db[_id]['phase'] != 'all' or db[_id]['function_name'] not in critical_path_functions:
            continue
        function_name = db[_id]['function_name']
        if function_name not in mx:
            mx[function_name] = db[_id]['time']
        else:
            mx[function_name] = max(mx[function_name], db[_id]['time'])
    for k, v in mx.items():
        crit_latency += v
    return crit_latency

def analyze_workflow(workflow_name):
    repo.clear_couchdb_results()
    repo.clear_redis_cache()
    repo.clear_couchdb_workflow_latency()
    total = 5
    ids = [str(uuid.uuid4()) for i in range(total)]
    e2e_total = 0
    crit_total = 0
    for i in range(total):
        id = ids[i]
        print('----firing workflow----', id)
        e2e_latency = run_workflow(workflow_name, id)
        if i >= 2:
            crit_latency = get_crit_latency(workflow_name, id)
            e2e_total += e2e_latency
            crit_total += crit_latency
            print('crit_latency: ', crit_latency, 'e2e_latency: ', e2e_latency)
    scheduling_overhead = (e2e_total - crit_total) / (total - 2)
    f.write(workflow_name + ': ' + str(scheduling_overhead) + '\n')
    f.flush()

def analyze():
    # workflow_pool = ['video', 'illgal_recognizer', 'fileprocessing', 'wordcount', 'cycles', 'epigenomics', 'genome', 'soykb']
    workflow_pool = ['video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    # workflow_pool = ['illgal_recognizer']
    for workflow in workflow_pool:
        analyze_workflow(workflow)

if __name__ == '__main__':
    analyze()