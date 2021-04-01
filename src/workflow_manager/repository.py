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


def create_result_db(request_id):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    couch.create('results_' + request_id)


def get_file_by_name(file_name, request_id):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['results_' + request_id]
    for item in db.find({'selector': {'file_name': file_name}}):
        return item


def put_file_info(file_info_list, request_id):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['results_' + request_id]
    for file_info in file_info_list:
        db.save(file_info)


def has_files(file_name_list, request_id):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['results_' + request_id]
    for file_name in file_name_list:
        if len(db.find({'selector': {'file_name': file_name}})) == 0:
            return False
    return True


def save_basic_input(input_file_list):
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['basic_input']
    for file in input_file_list:
        db.save({'file_name': file})


def get_basic_input():
    couch = couchdb.Server('http://admin:admin@localhost:5984')
    db = couch['basic_input']
    return db.find({})
