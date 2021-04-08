import couchdb

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'

def save_function_info(function_info_list):
    couch = couchdb.Server(couchdb_url)
    #print('create')
    if 'function_info' in couch:
        couch.delete('function_info')
    db = couch.create('function_info')
    #print('create end')
    for info in function_info_list:
        db.save(info)


def save_start_node_name(start_node_name):
	couch = couchdb.Server(couchdb_url)
	db = couch['function_info']
	db.save({'start_node_name': start_node_name})


def get_start_node_name():
	couch = couchdb.Server(couchdb_url)
	db = couch['function_info']
	for item in db:
		doc = db[item]
		if 'start_node_name' in doc:
			return doc['start_node_name']


def get_function_info(function_name):
    couch = couchdb.Server(couchdb_url)
    db = couch['function_info']
    for item in db.find({'selector': {'function_name': function_name}}):
        return item


def save_basic_input(input_file_list):
    couch = couchdb.Server(couchdb_url)
    if 'basic_input' in couch:
        couch.delete('basic_input')
    db = couch.create('basic_input')
    for file in input_file_list:
        db.save({'file_name': file})


def get_basic_input():
    couch = couchdb.Server(couchdb_url)
    db = couch['basic_input']
    res = []
    for doc in db:
        res.append(db[doc])
    return res

def prepare_basic_file(file_list):
    couch = couchdb.Server(couchdb_url)
    db = couch['results']
    for file in file_list:
        db[file['request_id'] + '_' + file['file_name']] = {'key': file['file_name'], 'value': file['value']}


def create_result_db():
    couch = couchdb.Server(couchdb_url)
    if "results" in couch:
        couch.delete("results")
    db = couch.create("results")
