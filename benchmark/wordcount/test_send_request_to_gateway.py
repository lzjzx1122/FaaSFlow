import datetime
import json
import os.path
import shutil

from gevent import monkey

monkey.patch_all()
import sys
import time
import gevent
import pandas as pd
import numpy as np

sys.path.append('../../')
import requests
from src.workflow_manager.repository import Repository
from config import config

repo = Repository()
gateway_url = 'http://' + config.GATEWAY_URL + '/{}'
slow_threshold = 0
pre_time = 20
test_time = 2 * 60
maximal_time = pre_time + test_time
parallel = 1
latencies = []
request_infos = {}
ids = {}


def post_request(request_id, idx):
    request_info = {'request_id': request_id,
                    'workflow_name': 'wordcount',
                    'input_datas': {'$USER.start': {'datatype': 'entity', 'val': None, 'output_type': 'NORMAL'}}}
    print('--firing--', request_id)
    st = time.time()
    r = requests.post(gateway_url.format('run'), json=request_info)
    ed = time.time()
    if st > test_start + pre_time:
        ids[request_id] = {'time': ed - st, 'st': st, 'ed': ed}
        latencies.append(ed - st)
    print(request_id, ed - st, r.json())


def end_loop(idx):
    while time.time() - test_start < maximal_time:
        post_request('request_' + str(idx).rjust(4, '0'), idx)
        idx += parallel


def get_use_container_log():
    cnt = {}
    avg = {}
    requests_logs = repo.get_latencies('use_container')
    save_logs = {}
    for request_id in ids:
        start_time = ids[request_id]['st']
        duration = ids[request_id]['time']
        slow = False
        if duration > slow_threshold:
            slow = True
        logs = requests_logs[request_id]
        save_logs[request_id] = {}
        save_logs[request_id]['logs'] = []
        save_logs[request_id]['fire_time'] = start_time
        if slow:
            print(ids[request_id])
        for log in logs:
            save_logs[request_id]['logs'].append({'time': log['time'], 'st': log['st'], 'ed': log['ed']})
            function_name = log['template_name'] + '_' + log['block_name']
            if function_name not in cnt:
                cnt[function_name] = 0
            cnt[function_name] += 1
            if function_name not in avg:
                avg[function_name] = [0, 0, 0]
            avg[function_name][0] += log['time']
            avg[function_name][1] += log['st'] - start_time
            avg[function_name][2] += log['ed'] - start_time
            if slow:
                print(function_name, "%0.3f" % log['time'], "%0.3f" % (log['st'] - start_time),
                      "%0.3f" % (log['ed'] - start_time))

    for function_name in cnt:
        print(function_name, end=' ')
        for v in avg[function_name]:
            print("%0.3f" % (v / cnt[function_name]), end=' ')
        print()
    nowtime = str(datetime.datetime.now())
    if not os.path.exists('result'):
        os.mkdir('result')
    filepath = os.path.join('result', nowtime + '_result.json')
    with open(filepath, 'w') as f:
        json.dump(save_logs, f)


def cal_percentile():
    percents = [50, 90, 95, 99]
    for percent in percents:
        print(f'P{percent}: ', format(np.percentile(latencies, percent), '.3f'))


repo.clear_couchdb_workflow_latency()
repo.clear_couchdb_results()
test_start = time.time()
events = []
for i in range(parallel):
    events.append(gevent.spawn_later(i * 2, end_loop, i))
for e in events:
    e.join()
get_use_container_log()
cal_percentile()
print(len(latencies))
print('avg e2e:', sum(latencies) / len(latencies))
