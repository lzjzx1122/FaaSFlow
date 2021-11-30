import json
import os
import threading
import time

class Store:
    def __init__(self, workflow_name, function_name, request_id, input, output, to, keys, runtime, db_server, redis_server):
        # to: where to store for outputs
        # keys: foreach key (split_key) specified by workflow_manager
        self.db = db_server['results']
        self.latency_db = db_server['workflow_latency']
        self.log_db = db_server['log']
        self.redis = redis_server
        self.fetch_dict = {}
        self.put_dict = {}
        self.workflow_name = workflow_name
        self.function_name = function_name
        self.request_id = request_id
        self.input = input
        self.output = output
        self.to = to
        self.keys = keys
        self.runtime = runtime
        if os.path.exists('work'):
            os.system('rm -rf work')
        os.mkdir('work')

    def fetch_from_mem(self, k, redis_key, content_type):
        if content_type == 'application/json':
            redis_value = self.redis[redis_key].decode()
            self.log_db.save({'request_id': self.request_id, 'workflow': self.workflow_name, 'function': self.function_name, 
                              'key': k, 'action': 'GET', 'size': len(redis_value)}) # save data-transfer log
            self.fetch_dict[k] = json.loads(redis_value)
        else:
            self.fetch_dict[k] = self.redis[redis_key]
            self.log_db.save({'request_id': self.request_id, 'workflow': self.workflow_name, 'function': self.function_name, 
                              'key': k, 'action': 'GET', 'size': len(self.fetch_dict[k])}) # save data-transfer log

    def fetch_from_db(self, k, param):
        f = self.db.get_attachment(self.request_id, filename=param, default='no attachment')
        if f != 'no attachment':
            self.fetch_dict[k] = f.read()
            self.log_db.save({'request_id': self.request_id, 'workflow': self.workflow_name, 'function': self.function_name, 
                              'key': k, 'action': 'GET', 'size': len(self.fetch_dict[k])}) # save data-transfer log
        else:
            filename = param + '.json'
            f = self.db.get_attachment(self.request_id, filename=filename, default='no attachment')
            if f == 'no attachment':
                self.fetch_dict[k] = f
            else:
                b = f.read()
                self.log_db.save({'request_id': self.request_id, 'workflow': self.workflow_name, 'function': self.function_name, 
                                  'key': k, 'action': 'GET', 'size': len(b)}) # save data-transfer log
                self.fetch_dict[k] = json.loads(b)

    # input_keys: specify the keys you want
    def fetch(self, input_keys):
        fetch_start = time.time()
        self.fetch_dict = {}
        threads = []
        for k in input_keys:
            if k in self.input:
                param = self.input[k]['parameter']  # supporting inputMapping
            else:
                param = k
            if param in self.keys:  # if it's a foreach key
                self.fetch_dict[k] = self.keys[param]
            else:  # regular keys
                redis_key_1 = self.request_id + '_' + param
                redis_key_2 = self.request_id + '_' + param + '.json'
                if redis_key_1 in self.redis:
                    thread_ = threading.Thread(target=self.fetch_from_mem, args=(k, redis_key_1, 'bytes'))
                elif redis_key_2 in self.redis:
                    thread_ = threading.Thread(target=self.fetch_from_mem, args=(k, redis_key_2, 'application/json'))
                else:  # if not
                    thread_ = threading.Thread(target=self.fetch_from_db, args=(k, param,))
                threads.append(thread_)
        for thread_ in threads:
            thread_.start()
        for thread_ in threads:
            thread_.join()
        fetch_end = time.time()
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': fetch_end - fetch_start})
        return self.fetch_dict

    def put_to_mem(self, k, content_type):
        if content_type == 'application/json':
            redis_key = self.request_id + '_' + k + '.json'
        else:
            redis_key = self.request_id + '_' + k
        self.redis[redis_key] = self.put_dict[k]

    def put_attachment_wrapper(self, k, content_type):
        try:
            filename = k
            if content_type == 'application/json':
                filename = filename + '.json'
            self.db.put_attachment(self.db[self.request_id], self.put_dict[k], filename=filename, content_type=content_type)            
            return 0
        except Exception:
            return 1

    def put_to_db(self, k, content_type):
        while self.put_attachment_wrapper(k, content_type) == 1:
            pass

    def put_keys(self, k):
        doc = self.db[self.request_id]
        doc[k] = self.put_dict[k]
        self.db.save(doc)

    # output_result: {'k1': ...(dict-like), 'k2': ...(byte stream)}
    # output_content_type: default application/json, just specify one when you need to
    def put(self, output_result, output_content_type):
        for k in output_result:
            if k not in output_content_type:
                output_content_type[k] = 'application/json'  # default: dict-like, should be stored in json style
        self.put_dict = output_result
        for k in output_result:
            if output_content_type[k] == 'application/json':
                if (k not in self.output) or (k in self.output and self.output[k]['type'] != 'keys'):
                    self.put_dict[k] = json.dumps(self.put_dict[k])
            self.log_db.save({'request_id': self.request_id, 'workflow': self.workflow_name, 'function': self.function_name, 
                              'key': k, 'action': 'PUT', 'size': len(self.put_dict[k])}) # save data-transfer log
        put_start = time.time()
        for k in output_result:
            if k in self.output and self.output[k]['type'] == 'keys':  # it's the keys for foreach
                self.put_keys(k)
        if 'DB' in self.to:
            for k in output_result:
                if k not in self.output or self.output[k]['type'] != 'keys':
                    self.put_to_db(k, output_content_type[k])
        if 'MEM' in self.to:
            for k in output_result:
                if k not in self.output or self.output[k]['type'] != 'keys':
                    self.put_to_mem(k, output_content_type[k])
        put_end = time.time()
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': put_end - put_start})
