import os
import sys
import time
import uuid
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
from typing import List

sys.path.append('../../')
from flask import Flask, request
from confluent_kafka import Consumer, TopicPartition
from config import config

proxy = Flask(__name__)
consumers: List[Consumer] = []


@proxy.route('/prefetch_data', methods=['post'])
def prefetch_data():
    # st = time.time()
    datainfo = request.get_json(force=True, silent=True)
    db_key = datainfo['db_key']
    partition_idx = datainfo['partition_idx']
    chunk_num = datainfo['chunk_num']
    topic = datainfo['topic']
    start_offset = datainfo['start_offset']
    # try:
    #     consumer = consumers.pop()
    # except Exception:
    consumer = Consumer({'bootstrap.servers': config.KAFKA_URL,
                         'group.id': str(uuid.uuid4()),
                         'enable.auto.commit': False})
    # print('assigning:', topic, partition_idx, start_offset)
    consumer.assign([TopicPartition(topic, partition_idx, offset=start_offset)])
    # print(consumer.assignment())
    # mid = time.time()
    # size = 0
    with open(os.path.join(config.PREFETCH_POOL_PATH, db_key), 'wb') as f:
        for i in range(chunk_num):
            # st = time.time()
            message = consumer.consume()[0]
            # while message.error():
            #     assert i == 0
            #     print(message.error())
            #     time.sleep(0.005)
            #     consumer.assign([TopicPartition(topic, partition_idx, offset=start_offset)])
            #     message = consumer.consume()[0]
            chunk_data = message.value()
            # tmp = json.loads(chunk_data)
            # print(db_key, tmp['db_key'], tmp['idx'], i, chunk_num)
            # chunk_data = tmp['val'].encode()
            # size += len(chunk_data)
            f.write(chunk_data)
            # expect_time = len(chunk_data) / 10485760
            # ed = time.time()
            # if config.KAFKA_CHUNK_TEST and ed - st < expect_time:
            #     time.sleep(expect_time - (ed - st))
    # ed = time.time()
    # consumer.unassign()
    # consumers.append(consumer)
    # print('prefetch time:', ed - st, 'prepare_time:', mid - st, 'size', size)
    return 'OK', 200


if __name__ == '__main__':
    proxy.run('0.0.0.0', 8002, threaded=True)
