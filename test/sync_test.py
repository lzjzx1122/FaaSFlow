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


def get_use_container_log(workflow_name, loop_cnt, tests_duration):
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
            save_logs[request_id]['logs'].append({'time': log['time'], 'function_name': function_name, 'st': log['st'], 'ed': log['ed']})

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
    suffix = 'sync_' + workflow_name + '_' + str(loop_cnt) + '_' + str(tests_duration) + f'_({input_args})'

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


def test_to_one(workflow_name, loop_cnt, duration):
    repo.clear_couchdb_workflow_latency()
    repo.clear_couchdb_results()
    r = requests.post(f'http://{config.GATEWAY_IP}:7000/clear')
    assert r.status_code == 200
    threads_ = []
    for addr in config.WORKER_ADDRS:
        t = threading.Thread(target=clean_worker, args=(addr, ))
        threads_.append(t)
        t.start()
    for t in threads_:
        t.join()
    global ids, latencies
    ids = {}
    latencies = []
    print(f'firing {workflow_name} with loop {loop_cnt} for {duration} s')
    global test_start
    test_start = time.time()
    events = []
    for i in range(loop_cnt):
        events.append(gevent.spawn_later(i * 2, end_loop, i, workflow_name, loop_cnt, duration))
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
    get_use_container_log(workflow_name, loop_cnt, duration)

    print('avg:', format(sum(latencies) / len(latencies), '.3f'))
    cal_percentile()



def test_to_all():
    print(input_args)
    target_workflow = {'recognizer': {1: 10, 2: 10, 4: 10, 8: 10, 9: 10, 10: 10, 11: 10, 12: 10},
                       'video': {1: 10, 2: 10, 4: 10, 8: 10, 16: 10, 24: 10, 30: 10, 32: 10},
                       'wordcount': {1: 5, 2: 5, 4: 5, 8: 5, 16: 5, 19: 5, 20: 5, 21: 5, 22: 5, 23: 5, 24: 5}}
    # target_workflow = {
    #     'recognizer': {11: 10, 12: 10, 13: 10},
    #     'video': {12: 10, 13: 10, 14: 10},
    #     'wordcount': {23: 5},
    #     }
    # target_workflow = {
    #     'video': {28: 10, 30: 10}}
    target_workflow = {'recognizer': {1: 1},
                       'video': {1: 1},
                       'svd': {1: 1},
                       'wordcount': {1: 1}}
    # target_workflow = {
    #                    'recognizer': {6: 10},
    #                    'video': {2: 10, 4: 10, 8: 10, 16: 10, 24: 10, 32: 10, 36: 10}}
    for workflow_name in target_workflow:
        for loop_cnt in target_workflow[workflow_name]:
            test_to_one(workflow_name, loop_cnt, 60 * target_workflow[workflow_name][loop_cnt])


test_to_all()
