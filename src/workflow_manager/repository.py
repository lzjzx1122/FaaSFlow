import couchdb


def save_function_info(function_info_list):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['function_info']
    for info in function_info_list:
        db.save(info)


def get_function_info(function_name):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['function_info']
    for item in db.find({'selector': {'function_name': function_name}}):
        return item


def save_basic_input(input_file_list):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['basic_input']
    for file in input_file_list:
        db.save({'file_name': file})


def get_basic_input():
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['basic_input']
    return db.find({})


def prepare_basic_file(file_list):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['basic_input']
    for file in file_list:
        db[file['request_id'] + '_' + file['file_name']] = {'key': file['file_name'], 'value': file['value']}
