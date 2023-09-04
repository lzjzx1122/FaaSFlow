import json
import os
import gc
import socket
import subprocess
import sys
import time
import uuid

import couchdb
import kafka
import requests
from flask import Flask, request
import threading
import queue
from multiprocessing import Process, Queue, Manager
import config
from block import Block
import bypass_store
from kafka import KafkaAdminClient
from kafka.admin.new_topic import NewTopic
import container_config

proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
# lock = threading.Lock()
work_dir = '/proxy'
blocks = Block.parse(config.BLOCKS_INFO_PATH)
# store_queue = Manager().Queue()
store_queue = queue.Queue()
# store_queue = []
kafka_topic_ids = [str(uuid.uuid4()) for i in range(container_config.KAFKA_NUM_TOPICS)]
admin = KafkaAdminClient(bootstrap_servers=container_config.KAFKA_URL)
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'


class Runner:
    def __init__(self):
        self.request_id = None
        self.workflow_name = None
        self.template_name = None
        self.function_info = None
        self.code = None
        self.ctx = None
        self.input_srcs = None
        self.idle_blocks = []
        self.cur_running = set()
        os.chdir(work_dir)
        # self.db = couchdb.Server('http://openwhisk:openwhisk@172.17.0.1:5984')['results']
        parallel_limit = len(blocks)
        for idx in range(parallel_limit):
            block_name = 'block_' + str(idx)
            os.mkdir(block_name)
            self.idle_blocks.append(block_name)

    def run_block(self, request_id, workflow_name, template_name, templates_infos, block_name, block_inputs: dict,
                  block_infos, chunk_size):
        assert block_name in blocks
        # lock.acquire()
        # if len(self.idle_blocks) == 0:
        #     print(self.cur_running)
        #     raise Exception('No idle blocks!')
        # # self.cur_running.add(request_id + '.' + block_name)
        # allocated_block = self.idle_blocks.pop()
        # lock.release()
        # store_queue = None
        block_work_dir = '/' + request_id + '_' + block_name
        delay_time = blocks[block_name].run(request_id, workflow_name, template_name, templates_infos, block_name,
                                            block_inputs, block_infos, block_work_dir, chunk_size, store_queue)
        return delay_time
        # p = Process(target=blocks[block_name].run,
        #             args=(request_id, workflow_name, template_name, templates_infos,
        #                   block_name, block_inputs, block_infos, block_work_dir, chunk_size, store_queue))
        # p.start()
        # p.join()
        # lock.acquire()
        # self.idle_blocks.append(allocated_block)
        # lock.release()


runner = Runner()


@proxy.route('/init', methods=['get'])
def init():
    inp = request.get_json(force=True, silent=True)
    limit_net = inp['limit_net']
    KAFKA_CHUNK_SIZE = inp['KAFKA_CHUNK_SIZE']
    if KAFKA_CHUNK_SIZE is not None:
        print('set KAFKA_CHUNK_SIZE to', KAFKA_CHUNK_SIZE)
        store.chunk_size = KAFKA_CHUNK_SIZE
    if limit_net:
        for block in blocks.values():
            block.cpu = inp['cpu']
        cpu = format(inp['cpu'], '.1f')
        script_path = f'/proxy/scripts/{cpu}.sh'
        subprocess.run(['bash', script_path, 'start'])

    return 'OK', 200


@proxy.route('/delete_topic', methods=['get'])
def delete_topic():
    # Todo: this can be done in the host.

    # admin.delete_topics(kafka_topic_ids)
    # admin.close()
    return 'OK', 200


@proxy.route('/post_data', methods=['POST'])
def post_data():
    st = time.time()
    val = request.get_data()
    data = json.loads(request.headers['json'])
    data['val'] = val
    store_queue.put(data)
    # store_queue.append(data)
    ed = time.time()
    print('proxy handle post_data time: ', ed - st, file=sys.stderr)
    return 'OK', 200


@proxy.route('/run_gc', methods=['POST'])
def run_gc():
    gc.collect()
    return 'OK', 200


@proxy.route('/run_block', methods=['POST'])
def run_block():
    # proxy.status = 'run'
    inp = request.get_json(force=True, silent=True)
    request_id = inp['request_id']
    workflow_name = inp['workflow_name']
    template_name = inp['template_name']
    templates_infos = inp['templates_infos']
    block_name = inp['block_name']
    block_inputs = inp['block_inputs']
    block_infos = inp['block_infos']
    chunk_size = inp['chunk_size']
    # print(request_id + ' ' + block_name + ' ' + 'start', file=sys.stderr)
    start = time.time()
    delay_time = runner.run_block(request_id, workflow_name, template_name, templates_infos, block_name, block_inputs,
                                  block_infos, chunk_size)
    end = time.time()
    # print(request_id + ' ' + block_name + ' ' + 'end', file=sys.stderr)
    # proxy.status = 'ok'
    return {'duration': end - start, 'delay_time': delay_time}


if __name__ == '__main__':
    admin.create_topics(
        [NewTopic(kafka_topic_id, container_config.KAFKA_NUM_PARTITIONS, 1) for kafka_topic_id in kafka_topic_ids])
    admin.close()
    store = bypass_store.Store()
    t = threading.Thread(target=store.get_block_output, args=(store_queue, kafka_topic_ids))
    t.start()
    proxy.run('0.0.0.0', 5000, threaded=True)
