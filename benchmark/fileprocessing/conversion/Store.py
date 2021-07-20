import json
import os
import threading

import couchdb
import redis

result_dir = "/results"


class Store:
    def __init__(self, function_name, request_id, input, output, to, keys):
        # to: where to store for outputs
        # keys: foreach key (split_key) specified by workflow_manager
        couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
        db_server = couchdb.Server(couchdb_url)
        self.db = db_server['results']
        self.redis = redis.StrictRedis(host='172.17.0.1', port=6380, db=0)
        self.fetch_dict = {}
        self.put_dict = {}
        # self.prefix = function_name + '_' + request_id
        self.function_name = function_name
        self.request_id = request_id
        self.input = input
        self.output = output
        self.to = to
        self.keys = keys
        if os.path.exists('work'):
            os.system('rm -rf work')
        os.mkdir('work')

    def fetch_from_mem(self, k, redis_key, content_type):
        # with open(path, 'r') as f:
        #     if content_type == 'application/json':
        #         self.fetch_dict[k] = json.load(f)
        #     else:
        #         self.fetch_dict[k] = f.read()
        if content_type == 'application/json':
            redis_value = self.redis[redis_key].decode()
            self.fetch_dict[k] = json.loads(redis_value)
        else:
            self.fetch_dict[k] = self.redis[redis_key]

    def fetch_from_db(self, k, param):
        f = self.db.get_attachment(self.request_id, filename=param, default='no attachment')
        if f != 'no attachment':
            self.fetch_dict[k] = f.read()
        else:
            filename = param + '.json'
            f = self.db.get_attachment(self.request_id, filename=filename, default='no attachment')
            self.fetch_dict[k] = json.load(f)

    # input_keys: specify the keys you want
    def fetch(self, input_keys):
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
        return self.fetch_dict

    def put_to_mem(self, k, content_type):
        if content_type == 'application/json':
            # path = os.path.join(result_dir, self.request_id + '_' + k + '.json')
            # with open(path, 'w') as f:
            #     json.dump(self.put_dict[k], f)
            redis_key = self.request_id + '_' + k + '.json'
            self.redis[redis_key] = json.dumps(self.put_dict[k])
        else:
            # path = os.path.join(result_dir, self.request_id + '_' + k)
            # with open(path, 'w') as f:
            #     f.write(self.put_dict[k])
            redis_key = self.request_id + '_' + k
            self.redis[redis_key] = self.put_dict[k]

    def put_attachment_wrapper(self, k, content_type):
        try:
            if content_type == 'application/json':
                filename = k + '.json'
                self.db.put_attachment(self.db[self.request_id], json.dumps(self.put_dict[k]), filename=filename, content_type=content_type)
            else:
                self.db.put_attachment(self.db[self.request_id], self.put_dict[k], filename=k, content_type=content_type)               
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
        # threads = []
        for k in output_result:
            if k in self.output and self.output[k]['type'] == 'keys':  # it's the keys for foreach
                self.put_keys(k)
                # thread_ = threading.Thread(target=self.put_keys, args=(k,))
                # threads.append(thread_)
        if 'DB' in self.to:
            for k in output_result:
                if k not in self.output or self.output[k]['type'] != 'keys':
                    self.put_to_db(k, output_content_type[k])
                    # thread_ = threading.Thread(target=self.put_to_db, args=(k, output_content_type[k]))
                    # threads.append(thread_)
        if 'MEM' in self.to:
            for k in output_result:
                if k not in self.output or self.output[k]['type'] != 'keys':
                    self.put_to_mem(k, output_content_type[k])
                    # thread_ = threading.Thread(target=self.put_to_mem, args=(k, output_content_type[k]))
                    # threads.append(thread_)
        # for thread_ in threads:
        #     thread_.start()
        # for thread_ in threads:
        #     thread_.join()

    # def naive_fetch(self, input):
    #     input_res = {}
    #     for (k, v) in input.items():
    #         if v['type'] == 'DB':
    #             doc = self.prefix + "_" + k
    #             input_res[k] = self.db[doc]['value']
    #         else:  # MEM
    #             path = self.prefix + "_" + k + ".json"
    #             with open(os.path.join(result_dir, path), "r") as f:
    #                 json_file = json.load(f)
    #                 input_res[k] = json_file['value']
    #     return input_res
    #
    # def naive_put(self, output, output_res):
    #     for (k, v) in output_res.items():
    #         if 'DB' in output[k]['type']:
    #             doc = self.prefix + "_" + k
    #             self.db[doc] = {"key": k, "value": v}
    #         if 'MEM' in output[k]['type']:
    #             path = self.prefix + "_" + k + ".json"
    #             json_file = {"key": k, "value": v}
    #             with open(os.path.join(result_dir, path), "w") as f:
    #                 json.dump(json_file, f)
