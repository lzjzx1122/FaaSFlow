import zipfile
import shutil
import os
import time
import re
import base64
import couchdb
import json
import threading
from flask import Flask, request
from gevent.pywsgi import WSGIServer

result_dir = "/results"


class Store:
    def __init__(self, function_name, request_id):
        couchdb_url = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
        db_server = couchdb.Server(couchdb_url)
        self.db = db_server['results']
        self.fetch_dict = {}
        self.put_dict = {}
        self.prefix = function_name + '_' + request_id
        self.function_name = function_name
        self.request_id = request_id

    def fetch_from_mem(self, function, parameter, key, action, foreach_id):
        if action == 'normal':
            path = os.path.join(result_dir, function + '_' + self.request_id + '_' + parameter + '.json')
            with open(path, 'r') as f:
                json_file = json.load(f)
                self.fetch_dict[key] = json_file['value']
        elif action == 'foreach':
            path = os.path.join(result_dir, function + '_' + self.request_id + '_' + parameter + '_' + foreach_id)
            with open(path, 'r') as f:
                self.fetch_dict[key] = f.read()
        elif action == 'merge':
            contents = []
            i = 0
            while True:
                path = os.path.join(result_dir, function + '_' + self.request_id + '_' + parameter + '_' + i)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        contents.append(f.read())
                    i = i + 1
                else:
                    break
            self.fetch_dict[key] = contents

    def fetch_from_db(self, function, parameter, key, action, foreach_id):
        doc = function + '_' + self.request_id + '_' + parameter
        if action == 'normal':
            self.fetch_dict[key] = self.db[doc]['value']
        elif action == 'foreach':
            r = self.db.get_attachment(self.db[doc], foreach_id)
            self.fetch_dict[key] = r.read()
        elif action == 'merge':
            contents = []
            i = 0
            while True:
                r = self.db.get_attachment(self.db[doc], i)
                if r is None:
                    break
                else:
                    contents.append(r.read())
                    i = i + 1
            self.fetch_dict[key] = contents

    def fetch(self, input, foreach_id):
        self.fetch_dict = {}
        threads = []
        for (k, v) in input.items():
            if v['type'] == 'DB':  # DB
                thread_ = threading.Thread(target=self.fetch_from_db,
                                           args=(v['function'], v['parameter'], k, v['action'], foreach_id,))
                threads.append(thread_)
            else:  # MEM
                thread_ = threading.Thread(target=self.fetch_from_mem,
                                           args=(v['function'], v['parameter'], k, v['action'], foreach_id))
                threads.append(thread_)
        for thread_ in threads:
            thread_.start()
        for thread_ in threads:
            thread_.join()
        return self.fetch_dict

    def put_to_mem(self, function, key, action, foreach_id):
        if action == 'normal':
            path = os.path.join(result_dir, function + '_' + self.request_id + '_' + key + '.json')
            with open(path, 'w') as f:
                json_file = {'key': key, 'value': self.put_dict[key]}
                json.dump(json_file, f)
        elif action == 'foreach':
            path = os.path.join(result_dir, function + '_' + self.request_id + '_' + key + '_' + foreach_id)
            with open(path, 'w') as f:
                json_file = {'key': key, 'value': self.put_dict[key]}
                json.dump(json_file, f)
        elif action == 'split':
            # let workflow manager know
            split_len = len(self.put_dict[key])
            doc = function + '_' + self.request_id + '_' + key
            self.db[doc] = {'key': key, 'len': split_len}
            for i in range(split_len):
                path = os.path.join(result_dir, function + '_' + self.request_id + '_' + key + '_' + i)
                with open(path, 'w') as f:
                    json_file = {'key': key, 'value': self.put_dict[key][i]}
                    json.dump(json_file, f)

    def put_to_db(self, function, key, action, foreach_id):
        doc = function + '_' + self.request_id + '_' + key
        if action == 'normal':
            self.db[doc] = {'key': key, 'value': self.put_dict[key]}
        # concurrently build doc?
        # couchdb update?
        elif action == 'foreach':
            if doc not in self.db:
                self.db[doc] = {'key': key}
            self.db.put_attachment(self.db[doc], self.put_dict[key], filename=foreach_id)
        elif action == 'split':
            split_len = len(self.put_dict[key])
            self.db[doc] = {'key': key, 'len': split_len}
            for i in range(split_len):
                self.db.put_attachment(self.db[doc], self.put_dict[key][i], filename=i)

    def put(self, output, output_res, foreach_id):
        self.put_dict = output_res
        threads = []
        for (k, v) in output.items():
            if 'DB' in v['type']:
                thread_ = threading.Thread(target=self.put_to_db, args=(self.function_name, k, v['action'], foreach_id))
                threads.append(thread_)
            if 'MEM' in v['type']:
                thread_ = threading.Thread(target=self.put_to_mem,
                                           args=(self.function_name, k, v['action'], foreach_id))
                threads.append(thread_)
        for thread_ in threads:
            thread_.start()
        for thread_ in threads:
            thread_.join()

    def naive_fetch(self, input):
        input_res = {}
        for (k, v) in input.items():
            if v['type'] == 'DB':
                doc = self.prefix + "_" + k
                input_res[k] = self.db[doc]['value']
            else:  # MEM
                path = self.prefix + "_" + k + ".json"
                with open(os.path.join(result_dir, path), "r") as f:
                    json_file = json.load(f)
                    input_res[k] = json_file['value']
        return input_res

    def naive_put(self, output, output_res):
        for (k, v) in output_res.items():
            if 'DB' in output[k]['type']:
                doc = self.prefix + "_" + k
                self.db[doc] = {"key": k, "value": v}
            if 'MEM' in output[k]['type']:
                path = self.prefix + "_" + k + ".json"
                json_file = {"key": k, "value": v}
                with open(os.path.join(result_dir, path), "w") as f:
                    json.dump(json_file, f)
