import couchdb
import redis
import json

couchdb_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'

class Repository:
    def __init__(self, workflow_name):
        self.redis = redis.StrictRedis(host='172.17.0.1', port=6380, db=0)
        self.couch = couchdb.Server(couchdb_url)
        db_list = [workflow_name + '_function_info', workflow_name + '_function_info_raw', workflow_name + '_workflow_metadata']
        for db_name in db_list:
            if db_name in self.couch:
                self.couch.delete(db_name)

    def save_function_info(self, function_info, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        for name in function_info:
            db[name] = function_info[name]

    def save_foreach_functions(self, foreach_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'foreach_functions': list(foreach_functions)})
    
    def save_merge_functions(self, merge_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'merge_functions': list(merge_functions)})

    def save_all_addrs(self, addrs, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'addrs': list(addrs)})

    def get_foreach_functions(self):
        db = self.couch['workflow_metadata']
        for item in db:
            doc = db[item]
            if 'foreach_functions' in doc:
                return doc['foreach_functions']

    def get_merge_functions(self):
        db = self.couch['workflow_metadata']
        for item in db:
            doc = db[item]
            if 'merge_functions' in doc:
                return doc['merge_functions']

    def save_start_functions(self, start_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'start_functions': start_functions})

    def get_start_node_name(self):
        db = self.couch['workflow_metadata']
        for item in db:
            doc = db[item]
            if 'start_node_name' in doc:
                return doc['start_node_name']

    def get_function_info(self, function_name, mode):
        db = self.couch[mode]
        for item in db.find({'selector': {'function_name': function_name}}):
            return item

    def save_basic_input(self, basic_input, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save(basic_input)

    def get_basic_input(self):
        db = self.couch['basic_input']
        res = None
        for doc in db:
            res = db[doc]
        return res

    # def prepare_basic_file(self, request_id, basic_file):
    #     db = self.couch['results']
    #     for k in basic_file:
    #         db['INPUT_' + request_id + '_' + k] = {'key': k, 'value': basic_file[k]}

    def create_request_doc(self, request_id):
        self.couch['results'][request_id] = {}

    def get_keys(self, request_id):
        keys = dict()
        doc = self.couch['results'][request_id]
        for k in doc:
            if k != '_id' and k != '_rev' and k != '_attachments':
                keys[k] = doc[k]
        return keys

    def get_len(self, request_id, function, parameter):
        db = self.couch['results']
        len = db[request_id + '_' + function + '_' + parameter]['len']
        return int(len)


    # fetch result from couchdb/redis
    def fetch_from_mem(self, redis_key, content_type):
        if content_type == 'application/json':
            redis_value = self.redis[redis_key].decode()
            return json.loads(redis_value)
        else:
            return self.redis[redis_key]

    def fetch_from_db(self, request_id, key):
        db = self.couch['results']
        f = db.get_attachment(request_id, filename=key, default='no attachment')
        if f != 'no attachment':
            return f.read()
        else:
            filename = key + '.json'
            f = db.get_attachment(request_id, filename=filename, default='no attachment')
            return json.load(f)

    def fetch(self, request_id, key):
        print('fetching...', key)
        redis_key_1 = request_id + '_' + key
        redis_key_2 = request_id + '_' + key + '.json'
        value = None
        if redis_key_1 in self.redis:
            value = self.fetch_from_mem(redis_key_1, 'bytes')
        elif redis_key_2 in self.redis:
            value = self.fetch_from_mem(redis_key_2, 'application/json')
        else:  # if not
            value = self.fetch_from_db(request_id, key)
        print('fetched value: ', value)
        return value
    
    def clear_mem(self, request_id):
        keys = self.redis.keys()
        for key in keys:
            key_str = key.decode()
            if key_str.startswith(request_id):
                self.redis.delete(key)
