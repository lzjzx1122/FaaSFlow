import couchdb


class Repository:
    def __init__(self, clear):
        couchdb_url = 'http://admin:admin@127.0.0.1:5984/'
        self.couch = couchdb.Server(couchdb_url)
        if clear:
            db_list = ['function_info', 'function_info_raw', 'workflow_metadata', 'basic_input', 'results']
            for db in db_list:
                if db in self.couch:
                    self.couch.delete(db)
                self.couch.create(db)

    def save_function_info(self, function_info_list, db_name):
        db = self.couch[db_name]
        for info in function_info_list:
            db.save(info)

    def save_foreach_functions(self, foreach_functions, db_name):
        db = self.couch[db_name]
        db.save({'foreach_functions': list(foreach_functions)})

    def get_foreach_functions(self):
        db = self.couch['workflow_metadata']
        for item in db:
            doc = db[item]
            if 'foreach_functions' in doc:
                return doc['foreach_functions']

    def save_start_node_name(self, start_node_name, db_name):
        db = self.couch[db_name]
        db.save({'start_node_name': start_node_name})

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

    def get_value(self, request_id, function, parameter):
        db = self.couch['results']
        value = db[request_id + '_' + function + '_' + parameter]['value']
        return int(value)

    def get_len(self, request_id, function, parameter):
        db = self.couch['results']
        len = db[request_id + '_' + function + '_' + parameter]['len']
        return int(len)
