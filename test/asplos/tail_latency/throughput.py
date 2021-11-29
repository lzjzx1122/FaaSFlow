from typing_extensions import final
from gevent import monkey; monkey.patch_all(thread=False)
import requests
from tqdm import tqdm
import repository
import gevent
import uuid
import time
# import prepare_basic_input
import sys

repo = repository.Repository()

speed = 400 # request / minute
latency_results = []
workflow_name = sys.argv[1]

def trigger_function(request_id, function_name):
    info = repo.get_function_info(function_name, workflow_name + '_function_info')
    url = 'http://{}/request'.format(info['ip'])
    data = {
        'request_id': request_id,
        'workflow_name': workflow_name,
        'function_name': function_name,
        'no_parent_execution': True
    }
    try:
        requests.post(url, json=data)
    except Exception:
        print('Exception Happend, Clearing...')
        master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
        clear_url = 'http://{}/clear'.format(master_addr)
        requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})

def run_workflow():
    global speed
    gevent.spawn_later(60 / speed, run_workflow)
    request_id = str(uuid.uuid4())
    repo.allocate_db(request_id)
    # print('----preparing input ', request_id, '----')
    # prepare_basic_input.prepare_basic_input(request_id)
    print('----dispatching request ', request_id, '----')
    start = time.time()
    start_functions = repo.get_start_functions(workflow_name + '_workflow_metadata')

    jobs = []
    for n in start_functions:
        jobs.append(gevent.spawn(trigger_function, request_id, n))
    gevent.joinall(jobs)
    master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
    clear_url = 'http://{}/clear'.format(master_addr)
    requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})
    end = time.time()
    print('----ending ', request_id, '----')
    latency_results.append(end - start)
    repo.save_latency(end - start)

def analyze():
    gevent.spawn_later(5, analyze)
    global latency_results
    print('!!!! we have ', len(latency_results), ' results by now !!!!')
    if len(latency_results) >= 20:
        print(latency_results[-10:])
    if len(latency_results) >= 110:
        results = latency_results[-105:]
        results.sort()
        print('max: ', results[-15:])
        # print('!!!! 95%: ', results[-5], ' 99%: ', results[-1], ' !!!!')

def run():
    global speed
    print('----running workflow ', speed, ' request / s----')
    repo.mem_clearall()
    repo.reset_all_mem(clear_function_data=True)
    repo.clear_latency_db()
    gevent.spawn_later(1, run_workflow)
    gevent.spawn_later(5, analyze)
    gevent.wait()

if __name__ == '__main__':
    # prepare()
    run()