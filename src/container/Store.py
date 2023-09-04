import json
import math
import os.path
import socket
import sys
import time
import threading
import couchdb
import redis
import requests
import container_config

host_url = 'http://172.17.0.1:8000/{}'
disk_reader_url = 'http://172.17.0.1:8001/{}'
db_threshold = 1024 * 16  # >16KB data will be sent to remote db
prefetch_path = '/proxy/mnt'


# Todo
#  Need a translator between function's predefined key_name and workflow's key_name!

class Store:
    def __init__(self, request_id, workflow_name, template_name, templates_infos, block_name, block_inputs: dict,
                 block_infos, chunk_size, store_queue, db, latency_db, redis_db):
        # self.cnt = 0
        self.db = db
        self.latency_db = latency_db
        self.redis = redis_db
        self.request_id = request_id
        self.workflow_name = workflow_name
        self.template_name = template_name
        self.templates_infos = templates_infos
        self.block_name = block_name
        self.block_inputs = block_inputs
        self.block_infos = block_infos
        self.chunk_size = chunk_size
        self.store_queue = store_queue
        self.block_outputs = {}
        self.outputs_type = {}
        self.fetch_dict = {}
        self.switch_status = 'NA'
        self.bypass_size = 0
        if self.block_infos['type'] == 'SWITCH':
            self.switch_status = 'PENDING'
        self.switch_branch = None
        self.block_serial = None
        for k, v in self.block_inputs.items():
            if 'output_type' in v and v['output_type'] == 'FOREACH':
                self.block_serial = v['serial_num']
        self.posting_threads = []
        self.outputs_serial = {}

    def fetch_scalability_config(self):
        try:
            data = self.db['scalability_config']
        except Exception:
            return None
        return data

    def post_to_disk(self, key, val, datatype, serial_num):
        assert datatype == 'json' or datatype == 'octet'
        filename = self.request_id + '.' + self.generate_db_key(key, serial_num)
        if datatype == 'octet':
            filepath = os.path.join(prefetch_path, filename)
            with open(filepath, 'wb') as f:
                f.write(val)
        elif datatype == 'json':
            filepath = os.path.join(prefetch_path, filename + '.json')
            with open(filepath, 'w') as f:
                f.write(val)
        else:
            raise Exception

    def generate_db_key(self, key, serial_num):
        return self.request_id + '.' + self.template_name + '.' + self.block_name + '.out.' + key + '.' + str(
            serial_num)

    def put_bigdata(self, key, val, datatype, serial_num):
        # Todo: potential problem: if couchdb is too slow, then the expired redis data will be uploaded to couchdb while
        #  this store is uploading to couchdb
        st = time.time()
        ips_cnt, local_cnt, remote_cnt, final_cnt = self.get_destination_locality(key)
        ed = time.time()
        # print('get_destination info', ed - st, file=sys.stderr)
        db_key = self.generate_db_key(key, serial_num)
        if datatype == 'json':
            db_key += '.json'
        if local_cnt > 0 or final_cnt > 0:
            # print('begin_put_to_redis', time.time() - start, file=sys.stderr)
            # st = time.time()
            self.put_to_redis(key, db_key, val, datatype, serial_num, local_cnt, remote_cnt)
            # ed = time.time()
            # print('put_to_redis', ed - st, file=sys.stderr)
            # t = threading.Thread(target=self.put_to_redis,
            #                      args=(key, db_key, val, datatype, serial_num, local_cnt, remote_cnt))
            # self.posting_threads.append(t)
            # t.start()
            # t.join()
        if remote_cnt > 0:
            # tmp = json.dumps({'request_id': self.request_id,
            #                   'workflow_name': self.workflow_name,
            #                   'template_name': self.template_name,
            #                   'block_name': self.block_name,
            #                   'key': key,
            #                   'db_key': db_key,
            #                   'datasize': len(val),
            #                   'datatype': datatype,
            #                   'switch_branch': self.switch_branch,
            #                   'serial_num': serial_num,
            #                   'output_type': self.block_infos['output_datas'][key]['type'],
            #                   'ips_cnt': ips_cnt,
            #                   'post_time': time.time()})
            # st = time.time()
            # requests.post('http://127.0.0.1:5000/post_data', data=val, headers={'json': tmp})
            # ed = time.time()
            # print('post_to_bypass_store time: ', ed - st, file=sys.stderr)
            self.store_queue.put({'request_id': self.request_id,
                                  'workflow_name': self.workflow_name,
                                  'template_name': self.template_name,
                                  'block_name': self.block_name,
                                  'key': key,
                                  'db_key': db_key,
                                  'val': val,
                                  'datasize': len(val),
                                  'datatype': datatype,
                                  'switch_branch': self.switch_branch,
                                  'serial_num': serial_num,
                                  'output_type': self.block_infos['output_datas'][key]['type'],
                                  'ips_cnt': ips_cnt,
                                  'post_time': time.time()})
            self.bypass_size += len(val)

    def put_to_redis(self, key, db_key, val, datatype, serial_num, local_cnt, remote_cnt):
        assert datatype == 'json' or datatype == 'octet'
        # st = time.time()
        self.redis[db_key] = val
        # ed = time.time()
        # print('redis post time consuming:', db_key, len(val), ed - st)
        # print('begin_post_to_host', time.time() - start, file=sys.stderr)
        # st = time.time()
        # t = threading.Thread(target=self.post_redis_data_ready_to_host,
        #                      args=(key, db_key, len(val), serial_num, local_cnt, remote_cnt))
        # self.posting_threads.append(t)
        # t.start()
        self.post_redis_data_ready_to_host(key, db_key, len(val), serial_num, local_cnt, remote_cnt)
        # ed = time.time()
        # print('host post time consuming:', db_key, ed - st)
        # print('ending', time.time() - start, file=sys.stderr)
        # self.redis.expire(db_key, 100)

    def put_to_couch(self, key, db_key, val, datatype, serial_num, ips_cnt):
        assert datatype == 'json' or datatype == 'octet'
        file_size = len(val)
        chunk_num = math.ceil(file_size / self.chunk_size)
        # doc = self.db[self.request_id]
        for i in range(chunk_num):
            chunk_val = val[(i * self.chunk_size):((i + 1) * self.chunk_size)]
            while True:
                try:
                    st = time.time()
                    self.db.put_attachment(self.db[self.request_id], chunk_val, filename=db_key + '.' + str(i),
                                           content_type='application/' + datatype)
                    ed = time.time()
                    # print('couchDB post time consuming:', key, ed - st, file=sys.stderr)
                    break
                except Exception as e:
                    print(e, file=sys.stderr)
                    time.sleep(0.05)
                    pass
            if i == 0:
                self.post_couch_data_ready_to_host(key, db_key, len(val), serial_num, ips_cnt, chunk_num)

    def post_couch_data_ready_to_host(self, key, db_key, size, serial_num, ips_cnt, chunk_num):
        post_data = {'request_id': self.request_id,
                     'workflow_name': self.workflow_name,
                     'template_name': self.template_name,
                     'block_name': self.block_name,
                     'datas': {key: {'datatype': 'couch_data_ready', 'datasize': size, 'db_key': db_key,
                                     'switch_branch': self.switch_branch, 'serial_num': serial_num,
                                     'output_type': self.block_infos['output_datas'][key]['type'],
                                     'ips_cnt': ips_cnt, 'chunk_num': chunk_num}},
                     'post_time': time.time()}
        requests.post(host_url.format('commit_inter_data'), json=post_data)

    def post_metadata_to_host(self, key, size, serial_num):
        post_data = {'request_id': self.request_id,
                     'workflow_name': self.workflow_name,
                     'template_name': self.template_name,
                     'block_name': self.block_name,
                     'datas': {key: {'datatype': 'metadata', 'datasize': size,
                                     'db_key': self.generate_db_key(key, serial_num),
                                     'switch_branch': self.switch_branch, 'serial_num': serial_num,
                                     'output_type': self.block_infos['output_datas'][key]['type']}},
                     'post_time': time.time()}
        requests.post(host_url.format('commit_inter_data'), json=post_data)

    def post_redis_data_ready_to_host(self, key, db_key, size, serial_num, local_cnt, remote_cnt):
        post_data = {'request_id': self.request_id,
                     'workflow_name': self.workflow_name,
                     'template_name': self.template_name,
                     'block_name': self.block_name,
                     'datas': {key: {'datatype': 'redis_data_ready', 'datasize': size, 'db_key': db_key,
                                     'local_cnt': local_cnt, 'remote_cnt': remote_cnt,
                                     'switch_branch': self.switch_branch, 'serial_num': serial_num,
                                     'output_type': self.block_infos['output_datas'][key]['type']}},
                     'post_time': time.time()}
        s = socket.socket()
        s.connect(('172.17.0.1', 5999))
        s.sendall(bytes(json.dumps(post_data), encoding='UTF-8'))
        s.close()
        # st = time.time()
        # requests.post(host_url.format('commit_inter_data'), json=post_data)
        # ed = time.time()
        # print('host post time consuming:', db_key, ed - st, file=sys.stderr)

    def post_data_fetched_to_host(self, db_key):
        # Todo: this message can be batched
        post_data = {'request_id': self.request_id,
                     'workflow_name': self.workflow_name,
                     'template_name': self.template_name,
                     'block_name': self.block_name,
                     'datas': {db_key: {'datatype': 'data_fetched', 'db_key': db_key}},
                     'post_time': time.time()}
        s = socket.socket()
        s.connect(('172.17.0.1', 5999))
        s.sendall(bytes(json.dumps(post_data), encoding='UTF-8'))
        s.close()
        # requests.post(host_url.format('commit_inter_data'), json=post_data)

    def post_direct_to_host(self, k, v, datatype, serial_num):
        if datatype == 'octet':
            v = bytes.decode(v)
            datatype = 'base64'
        post_data = {'request_id': self.request_id,
                     'workflow_name': self.workflow_name,
                     'template_name': self.template_name,
                     'block_name': self.block_name,
                     'datas': {k: {'datatype': datatype, 'val': v, 'switch_branch': self.switch_branch,
                                   'serial_num': serial_num,
                                   'output_type': self.block_infos['output_datas'][k]['type']}},
                     'post_time': time.time()}
        s = socket.socket()
        s.connect(('172.17.0.1', 5999))
        s.sendall(bytes(json.dumps(post_data), encoding='UTF-8'))
        s.close()
        # requests.post(host_url.format('commit_inter_data'), json=post_data)
        # print('put_direct_to_host finished!', k, file=sys.stderr)

    def handle_switch(self):
        for condition in self.block_infos['conditions']:
            if condition == 'default' or eval(condition, self.block_outputs):
                self.switch_branch = condition
                break
        for key in self.block_infos['conditions'][self.switch_branch]:
            if key.startswith('virtual'):
                self.block_outputs[key] = 'ok'
                self.outputs_type[key] = 'json'
                self.block_infos['output_datas'][key] = {'type': 'NORMAL'}
            self.post(key, self.block_outputs[key], datatype=self.outputs_type[key])

    def is_affinity_possible(self, key):
        # Todo: This result can be pre-calculated!
        dest = None
        if self.block_infos['type'] == 'SWITCH':
            dest = self.block_infos['conditions'][self.switch_branch][key]
        elif self.block_infos['type'] == 'NORMAL':
            dest = self.block_infos['output_datas'][key]['dest']
        for dest_template_name in dest.keys():
            if dest_template_name == self.template_name:
                return True
        return False

    def get_destination_locality(self, key):
        # Todo: This can be pre-calculated
        dest = None
        local_cnt = 0
        remote_cnt = 0
        final_cnt = 0
        ips_cnt = {}
        if self.block_infos['type'] == 'SWITCH':
            dest = self.block_infos['conditions'][self.switch_branch][key]
        elif self.block_infos['type'] == 'NORMAL':
            dest = self.block_infos['output_datas'][key]['dest']
        local_ip = self.templates_infos[self.template_name]['ip']
        for dest_template_name, dest_template_infos in dest.items():
            if dest_template_name == '$USER':
                final_cnt += 1
                continue
            target_ip = self.templates_infos[dest_template_name]['ip']
            if target_ip == local_ip:
                local_cnt += len(dest_template_infos)
            else:
                remote_cnt += len(dest_template_infos)
            if target_ip not in ips_cnt:
                ips_cnt[target_ip] = 0
            ips_cnt[target_ip] += len(dest_template_infos)
        return ips_cnt, local_cnt, remote_cnt, final_cnt

    def post(self, key, val, force=False, datatype='json', debug=False):
        if debug:
            st = val['st']
            ed = val['ed']
            self.latency_db.save({'request_id': self.request_id, 'template_name': self.template_name,
                                  'block_name': self.block_name + f'_{key}', 'phase': 'use_container',
                                  'time': ed - st, 'st': st, 'ed': ed})
            return
        assert datatype == 'json' or datatype == 'octet'
        if key not in self.outputs_serial:
            self.outputs_serial[key] = 0
        else:
            self.outputs_serial[key] += 1
        serial_num = self.outputs_serial[key]
        if self.block_serial is not None:
            serial_num = self.block_serial
        # Note: A switch block can't handle foreach output!!!
        if self.switch_status == 'PENDING':
            self.block_outputs[key] = val
            self.outputs_type[key] = datatype
            if len(self.block_outputs) == len(self.block_infos['output_datas']):
                self.switch_status = 'READY'
                self.handle_switch()
            return
        # print('POST', key, file=sys.stderr)
        val_db = val
        if datatype == 'json':
            val_db = json.dumps(val)
        size = len(val_db)
        if size > db_threshold or datatype == 'octet':
            # print('enter_put_bitdata', time.time() - start, file=sys.stderr)
            self.put_bigdata(key, val_db, datatype, serial_num)
        else:
            self.post_direct_to_host(key, val, datatype, serial_num)
            # t = threading.Thread(target=self.post_direct_to_host, args=(key, val, datatype, serial_num))
            # self.posting_threads.append(t)
            # t.start()

    def fetch(self, keys):
        self.fetch_dict = {}
        threads = []
        for k in keys:
            self.get_input_data(k, self.block_infos['input_datas'][k]['type'])
            # threads.append(
            #     threading.Thread(target=self.get_input_data, args=(k, self.block_infos['input_datas'][k]['type'])))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return self.fetch_dict

    def get_input_data(self, key, datatype='NORMAL'):
        if key not in self.block_inputs:
            raise Exception('no such input_data: ', key)
        if datatype == 'NORMAL':
            self.fetch_dict[key] = self.fetch_input_data(key, self.block_inputs[key])
        elif datatype == 'LIST':
            # This data is a merged list after foreach
            self.fetch_dict[key] = []
            for i in range(len(self.block_inputs[key])):
                # st = time.time()
                self.fetch_dict[key].append(self.fetch_input_data(key, self.block_inputs[key][str(i)]))
                # ed = time.time()
                # print(i, ed - st, file=sys.stderr)
        else:
            raise Exception

    def fetch_input_data(self, key, data_infos):
        datatype = data_infos['datatype']
        if datatype == 'redis_data_ready':
            return self.fetch_from_redis(data_infos['db_key'])
        elif datatype == 'couch_data_ready':
            return self.fetch_from_couch(data_infos['db_key'])
        elif datatype == 'json' or datatype == 'octet':
            return data_infos['val']
        elif datatype == 'disk_data_ready':
            return self.fetch_from_disk(data_infos['db_key'])
        else:
            raise Exception

    def fetch_from_disk(self, key):
        st = time.time()
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect('/proxy/mnt/transfer.sock')
        request_info = {'db_key': key}
        s.sendall(bytes(json.dumps(request_info), encoding='UTF-8'))
        data = []
        chunk = s.recv(container_config.SOCKET_CHUNK_SIZE)
        while chunk:
            data.append(chunk)
            chunk = s.recv(container_config.SOCKET_CHUNK_SIZE)
        s.close()
        data = b''.join(data)
        ed = time.time()
        # print('socket fetch from disk', ed - st, file=sys.stderr)
        self.post_data_fetched_to_host(key)
        # r = requests.get(disk_reader_url.format('fetch_from_disk'), json={'db_key': key})
        # t = threading.Thread(target=self.post_data_fetched_to_host, args=(key,))
        # self.posting_threads.append(t)
        # t.start()
        if key[-4:] == 'json':
            return json.loads(data)
        else:
            return data

    def fetch_from_redis(self, key):
        # print('fetching_from_redis:', key, file=sys.stderr)
        val = None
        if key[-4:] == 'json':
            try:
                val = json.loads(self.redis[key].decode())
            except Exception:
                pass
        else:
            try:
                val = self.redis[key]
            except Exception:
                pass
        if val is not None:
            self.post_data_fetched_to_host(key)
            # t = threading.Thread(target=self.post_data_fetched_to_host, args=(key,))
            # self.posting_threads.append(t)
            # t.start()
            return val
        print('fetch_from_redis failed:', key, file=sys.stderr)
        return self.fetch_from_disk(key)

    def fetch_from_couch(self, key):
        if key[-4:] == 'json':
            return json.loads(self.db.get_attachment(self.request_id, filename=key, default='no attachment').read())
        else:
            return self.db.get_attachment(self.request_id, filename=key, default='no attachment').read()
        # octet_data = self.db.get_attachment(self.request_id, filename=key, default='no attachment')
        # if octet_data != 'no attachment':
        #     print(type(octet_data), file=sys.stderr)
        #     return octet_data.read()
        # else:
        #     return json.loads(self.db.get_attachment(self.request_id, filename=key + '.json', default='no attachment'))
