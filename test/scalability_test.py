import datetime
import json
import os.path
import shutil
import threading

from gevent import monkey

monkey.patch_all()
import sys
import time
import gevent
import pandas as pd
import numpy as np

sys.path.append('../')
import requests
from src.workflow_manager.repository import Repository
from config import config

repo = Repository()
gateway_url = 'http://' + config.GATEWAY_URL + '/{}'
slow_threshold = 1000
pre_time = 2 * 60
latencies = []
request_infos = {}
ids = {}


def post_request(request_id, workflow_name):
    request_info = {'request_id': request_id,
                    'workflow_name': workflow_name,
                    'input_datas': {'$USER.start': {'datatype': 'entity', 'val': None, 'output_type': 'NORMAL'}}}
    # print('--firing--', request_id)
    st = time.time()
    r = requests.post(gateway_url.format('run'), json=request_info)
    ed = time.time()
    if st > test_start + pre_time:
        ids[request_id] = {'time': ed - st, 'st': st, 'ed': ed, 'latency': r.json()['latency']}
        latencies.append(r.json()['latency'])
    # print(request_id, ed - st, r.json())


def end_loop(idx, workflow_name, parallel, duration):
    while time.time() - test_start < pre_time + duration:
        post_request('request_' + str(idx).rjust(4, '0'), workflow_name)
        idx += parallel


input_args = ''.join(sys.argv[1:])


def get_use_container_log(suffix):
    cnt = {}
    avg = {}
    redis_logs = repo.get_latencies('redis')
    requests_logs = repo.get_latencies('use_container')
    save_logs = {}
    total_redis = 0
    for request_id in ids:
        # Calculate redis time
        if request_id in redis_logs:
            for log in redis_logs[request_id]:
                total_redis += log['time'] * log['size']

        # Calculate e2e and container time
        start_time = ids[request_id]['st']
        duration = ids[request_id]['time']
        slow = False
        if duration > slow_threshold:
            slow = True
        logs = requests_logs[request_id]
        save_logs[request_id] = {}
        save_logs[request_id]['logs'] = []
        save_logs[request_id]['fire_time'] = start_time
        save_logs[request_id]['latency'] = ids[request_id]['latency']
        if slow:
            print(ids[request_id])
        current_request_cnt = {}
        current_request_function_max_log = {}
        for log in logs:
            function_name = log['template_name'] + '_' + log['block_name']
            save_logs[request_id]['logs'].append(
                {'time': log['time'], 'function_name': function_name, 'st': log['st'], 'ed': log['ed']})

            if function_name not in current_request_cnt:
                current_request_cnt[function_name] = 0
            current_request_cnt[function_name] += 1
            if current_request_cnt[function_name] == 1:
                current_request_function_max_log[function_name] = log
            else:
                if log['time'] > current_request_function_max_log[function_name]['time']:
                    current_request_function_max_log[function_name] = log

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
        for func in current_request_cnt:
            if current_request_cnt[func] > 1:
                function_name = func + '_longest'
                log = current_request_function_max_log[func]
                if function_name not in cnt:
                    cnt[function_name] = 0
                cnt[function_name] += 1
                if function_name not in avg:
                    avg[function_name] = [0, 0, 0]
                avg[function_name][0] += log['time']
                avg[function_name][1] += log['st'] - start_time
                avg[function_name][2] += log['ed'] - start_time

    for function_name in cnt:
        print(function_name, end=' ')
        for v in avg[function_name]:
            print("%0.3f" % (v / cnt[function_name]), end=' ')
        print()
    print('Redis_KB-s:', format(total_redis / len(latencies), '.0f'))
    nowtime = str(datetime.datetime.now())
    if not os.path.exists('result'):
        os.mkdir('result')
    # suffix = 'sync_' + workflow_name + '_' + str(loop_cnt) + '_' + str(tests_duration) + f'_({input_args})'

    filepath = os.path.join('result', nowtime + '_' + suffix + '.json')
    with open(filepath, 'w') as f:
        json.dump(save_logs, f)


def cal_percentile():
    percents = [50, 90, 95, 99]
    for percent in percents:
        print(f'P{percent}: ', format(np.percentile(latencies, percent), '.3f'))


def clean_worker(addr):
    r = requests.post(f'http://{addr}:7999/clear')
    assert r.status_code == 200


def finish_worker(addr):
    r = requests.post(f'http://{addr}:8000/finish')
    assert r.status_code == 200


def test_to_one(workflow_name, config_type, para, duration):
    repo.clear_couchdb_workflow_latency()
    repo.clear_couchdb_results()
    r = requests.post(f'http://{config.GATEWAY_IP}:7000/clear')
    assert r.status_code == 200
    threads_ = []
    for addr in config.WORKER_ADDRS:
        t = threading.Thread(target=clean_worker, args=(addr,))
        threads_.append(t)
        t.start()
    for t in threads_:
        t.join()
    repo.save_scalability_config(f'/scalability/{config_type}_{para}/')
    global ids, latencies
    ids = {}
    latencies = []
    print(f'firing scalability with {config_type}_{para} for {duration} s')
    global test_start
    test_start = time.time()
    events = []
    events.append(gevent.spawn_later(0, end_loop, 0, workflow_name, 1, duration))
    for e in events:
        e.join()
    time.sleep(10)

    threads_ = []
    for addr in config.WORKER_ADDRS:
        t = threading.Thread(target=finish_worker, args=(addr,))
        threads_.append(t)
        t.start()
    for t in threads_:
        t.join()

    print('total requests count:', len(latencies))
    suffix = 'scalability_' + config_type + '_' + str(para) + '_' + str(duration) + f'_({input_args})'
    get_use_container_log(suffix)

    print('avg:', format(sum(latencies) / len(latencies), '.3f'))
    cal_percentile()
    # nowtime = str(datetime.datetime.now())
    # if not os.path.exists('result'):
    #     os.mkdir('result')
    # suffix = 'scalability_' + config_type + '_' + str(para) + '_' + str(duration) + f'_({input_args})'
    #
    # filepath = os.path.join('result', nowtime + '_' + suffix + '.json')
    # with open(filepath, 'w') as f:
    #     json.dump(latencies, f)


def test_to_all():
    print(input_args)
    target_config = {
        'fanout': {2, 4, 8, 12, 16},
        'datasize': {1, 2, 4, 8, 16}}
    for config_type in target_config:
        for para in target_config[config_type]:
            test_to_one('wordcount', config_type, para, 60 * 5)


test_to_all()
