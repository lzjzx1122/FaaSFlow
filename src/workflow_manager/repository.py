import couchdb

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'


def save_function_info(function_info_list, db_name):
    couch = couchdb.Server(couchdb_url)
    # print('create')
    if db_name in couch:
        couch.delete(db_name)
    db = couch.create(db_name)
    # print('create end')
    for info in function_info_list:
        db.save(info)


def save_start_node_name(start_node_name, db_name):
    couch = couchdb.Server(couchdb_url)
    db = couch[db_name]
    db.save({'start_node_name': start_node_name})


def get_start_node_name():
    couch = couchdb.Server(couchdb_url)
    db = couch['function_info']
    for item in db:
        doc = db[item]
        if 'start_node_name' in doc:
            return doc['start_node_name']


def get_function_info(function_name, mode):
    couch = couchdb.Server(couchdb_url)
    db = couch[mode]
    for item in db.find({'selector': {'function_name': function_name}}):
        return item


def save_basic_input(basic_input):
    couch = couchdb.Server(couchdb_url)
    if 'basic_input' in couch:
        couch.delete('basic_input')
    db = couch.create('basic_input')
    db.save(basic_input)


def get_basic_input():
    couch = couchdb.Server(couchdb_url)
    db = couch['basic_input']
    res = None
    for doc in db:
        res = db[doc]
    return res


def prepare_basic_file(request_id, basic_file):
    couch = couchdb.Server(couchdb_url)
    db = couch['results']
    db[request_id + '_INPUT'] = basic_file


def create_result_db():
    couch = couchdb.Server(couchdb_url)
    if "results" in couch:
        couch.delete("results")
    db = couch.create("results")


def get_value(request_id, function, parameter):
    couch = couchdb.Server(couchdb_url)
    db = couch['results']
    value = db[request_id + '_' + function][parameter]
    return int(value)

# db[request_id + '_' + function] = {parameter: value}
