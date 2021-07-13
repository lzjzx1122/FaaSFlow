import couchdb
import json

couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
def prepare_basic_input(request_id):
    db_server = couchdb.Server(couchdb_url)
    db = db_server['workflow_metadata']
    results_db = db_server['results']
    if request_id in results_db:
        results_db.delete(results_db[request_id])
    results_db[request_id] = {}
    for item in db:
        doc = db[item]
        if 'start_functions' not in doc and 'foreach_functions' not in doc and 'merge_functions' not in doc:
            for k in doc:
                if k == '_id' or k == '_rev':
                    continue
                content = 'a' * int(doc[k])
                filename = k + '.json'
                results_db.put_attachment(results_db[request_id], content, filename=filename)
prepare_basic_input('123')
