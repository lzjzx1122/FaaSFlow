import json
import math
import socket
import sys
import threading
import time
import queue
import couchdb
import requests
import container_config
import multiprocessing
from confluent_kafka import Producer

host_url = 'http://172.17.0.1:8000/{}'


# Todo
#  Need a translator between function's predefined key_name and workflow's key_name!

class Store:
    def __init__(self):
        # self.cnt = 0
        self.kafka_topic_ids = None
        self.db = couchdb.Server(container_config.COUCHDB_URL)['results']
        self.chunk_size = container_config.KAFKA_CHUNK_SIZE
        self.kafka_producer = None
        self.topics_partitions_offset = {}

    def put_to_kafka(self, data_info, topic, topic_idx, partition_idx):
        request_id = data_info['request_id']
        datatype = data_info['datatype']
        db_key = data_info['db_key']
        if db_key[-4:] == 'json':
            data_info['val'] = data_info['val'].encode()
        val = data_info['val']
        assert datatype == 'json' or datatype == 'octet'
        start_offset = self.topics_partitions_offset[topic_idx][partition_idx]
        file_size = len(val)
        chunk_num = math.ceil(file_size / self.chunk_size)
        # doc = self.db[self.request_id]
        for i in range(chunk_num):
            chunk_val = val[(i * self.chunk_size):((i + 1) * self.chunk_size)]
            while True:
                try:
                    # print(db_key, i, chunk_num, file=sys.stderr)
                    # st = time.time()
                    # chunk_val = json.dumps({'db_key': db_key, 'idx': i, 'val': str(chunk_val)}).encode()
                    # self.kafka_producer.send(self.kafka_topic_id, chunk_val)  # kafka-python
                    # self.kafka_producer.produce(chunk_val)
                    self.kafka_producer.produce(topic, chunk_val, partition=partition_idx)  # confluent-kafka
                    # ed = time.time()
                    # print('couchDB post time consuming:', key, ed - st, file=sys.stderr)
                    break
                except Exception as e:
                    print('---', e, file=sys.stderr)
                    time.sleep(0.05)
                    pass
            if i == 0:
                self.kafka_producer.flush()
                self.post_kafka_data_ready_to_host(data_info, topic, partition_idx, start_offset, chunk_num)
        # Todo: maybe flush() is slow and we need to use poll() after per produce()
        self.kafka_producer.flush()
        self.topics_partitions_offset[topic_idx][partition_idx] += chunk_num

    def post_kafka_data_ready_to_host(self, data_info, topic, partition_idx, start_offset, chunk_num):
        post_data = {'request_id': data_info['request_id'],
                     'workflow_name': data_info['workflow_name'],
                     'template_name': data_info['template_name'],
                     'block_name': data_info['block_name'],
                     'datas': {data_info['key']: {'datatype': 'kafka_data_ready', 'datasize': data_info['datasize'],
                                                  'db_key': data_info['db_key'],
                                                  'switch_branch': data_info['switch_branch'],
                                                  'serial_num': data_info['serial_num'],
                                                  'output_type': data_info['output_type'],
                                                  'ips_cnt': data_info['ips_cnt'],
                                                  'topic': topic,
                                                  'partition_idx': partition_idx,
                                                  'start_offset': start_offset,
                                                  'chunk_num': chunk_num}},
                     'post_time': time.time()}
        s = socket.socket()
        s.connect(('172.17.0.1', 5999))
        s.sendall(bytes(json.dumps(post_data), encoding='UTF-8'))
        s.close()
        # requests.post(host_url.format('commit_inter_data'), json=post_data)

    def put_to_couch(self, datainfo):
        datatype = datainfo['datatype']
        assert datatype == 'json' or datatype == 'octet'
        request_id = datainfo['request_id']
        db_key = datainfo['db_key']
        val = datainfo['val']
        file_size = len(val)
        while True:
            try:
                self.db.put_attachment(self.db[request_id], val, filename=db_key,
                                       content_type='application/' + datatype)
                break
            except Exception as e:
                print(e, file=sys.stderr)
                time.sleep(0.05)
                pass
        self.post_couch_data_ready_to_host(datainfo)

    def post_couch_data_ready_to_host(self, datainfo):
        post_data = {'request_id': datainfo['request_id'],
                     'workflow_name': datainfo['workflow_name'],
                     'template_name': datainfo['template_name'],
                     'block_name': datainfo['block_name'],
                     'datas': {datainfo['key']: {'datatype': 'couch_data_ready', 'datasize': datainfo['datasize'],
                                                 'db_key': datainfo['db_key'],
                                                 'switch_branch': datainfo['switch_branch'],
                                                 'serial_num': datainfo['serial_num'],
                                                 'output_type': datainfo['output_type'],
                                                 'ips_cnt': datainfo['ips_cnt']}},
                     'post_time': time.time()}
        requests.post(host_url.format('commit_inter_data'), json=post_data)

    def dispatch(self, q: queue.Queue):
        kafka_topic_idx = 0
        kafka_partition_idx = 0
        while True:
            data_info = q.get()
            if container_config.REMOTE_DB == 'KAFKA':
                # Todo: limiting sub-thread number!
                topic = self.kafka_topic_ids[kafka_topic_idx]
                t = threading.Thread(target=self.put_to_kafka,
                                     args=(data_info, topic, kafka_topic_idx, kafka_partition_idx))
                t.start()
                t.join()
                # self.put_to_kafka(data_info, kafka_partition_idx)
                kafka_topic_idx += 1
                if kafka_topic_idx == container_config.KAFKA_NUM_TOPICS:
                    kafka_topic_idx = 0
                    kafka_partition_idx += 1
                    if kafka_partition_idx == container_config.KAFKA_NUM_PARTITIONS:
                        kafka_partition_idx = 0
            elif container_config.REMOTE_DB == 'COUCH':
                self.put_to_couch(data_info)
            else:
                raise Exception

    def get_block_output(self, process_queue: queue.Queue, kafka_topic_ids):
        for i in range(container_config.KAFKA_NUM_TOPICS):
            self.topics_partitions_offset[i] = {}
            for j in range(container_config.KAFKA_NUM_PARTITIONS):
                self.topics_partitions_offset[i][j] = 0
        # thread_queue = queue.Queue()
        kafka_topic_idx = 0
        kafka_partition_idx = 0
        self.kafka_topic_ids = kafka_topic_ids
        self.kafka_producer = Producer({'bootstrap.servers': container_config.KAFKA_URL,
                                        'enable.idempotence': True})
        # threading.Thread(target=self.dispatch, args=(process_queue,)).start()

        # client = pykafka.KafkaClient(hosts=container_config.KAFKA_URL)
        # kafka_topic: pykafka.topic.Topic = client.topics[kafka_topic_id]
        # self.kafka_producer = kafka_topic.get_producer(sync=True, linger_ms=0)
        # self.kafka_producer = KafkaProducer(bootstrap_servers=container_config.KAFKA_URL)
        while True:
            # if len(process_queue) > 0:
            if True:
                # data_info = process_queue.pop(0)
                data_info = process_queue.get()
                # print('transfer_time:', time.time() - data_info['post_time'], 'db_key:', data_info['db_key'],
                #       'file_size:', data_info['datasize'])
                # thread_queue.put(data_info)
                st = time.time()
                if container_config.REMOTE_DB == 'KAFKA':
                    # Todo: limiting sub-thread number!
                    topic = self.kafka_topic_ids[kafka_topic_idx]
                    self.put_to_kafka(data_info, topic, kafka_topic_idx, kafka_partition_idx)
                    # t = threading.Thread(target=self.put_to_kafka,
                    #                      args=(data_info, topic, kafka_topic_idx, kafka_partition_idx))
                    # t.start()
                    # t.join()
                    kafka_topic_idx += 1
                    if kafka_topic_idx == container_config.KAFKA_NUM_TOPICS:
                        kafka_topic_idx = 0
                        kafka_partition_idx += 1
                        if kafka_partition_idx == container_config.KAFKA_NUM_PARTITIONS:
                            kafka_partition_idx = 0
                elif container_config.REMOTE_DB == 'COUCH':
                    self.put_to_couch(data_info)
                else:
                    raise Exception
                ed = time.time()
                # print('post_to_remote time:', ed - st, 'db_key:', data_info['db_key'],
                #       'file_size:', data_info['datasize'])
            else:
                time.sleep(0.05)
