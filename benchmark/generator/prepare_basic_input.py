import couchdb
import json
import gevent
from gevent import monkey
monkey.patch_all()

couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
request_id = '123'
db_server = couchdb.Server(couchdb_url)
db = db_server['workflow_metadata']
results_db = db_server['results']
if request_id in results_db:
    results_db.delete(results_db[request_id])
results_db[request_id] = {}

def put_attachment_wrapper(request_id, byte_cnt, filename):
    try:
        content = 'a' * byte_cnt   
        results_db.put_attachment(results_db[request_id], content, filename=filename)
        return 0
    except Exception:
        return 1

def put_attachment_loop(request_id, byte_cnt, filename):
    print(filename)
    while put_attachment_wrapper(request_id, byte_cnt, filename) == 1:
        pass

def prepare_basic_input():
    jobs = []
    for item in db:
        doc = db[item]
        if 'start_functions' not in doc and 'foreach_functions' not in doc and 'merge_functions' not in doc:
            for k in doc:
                if k == '_id' or k == '_rev':
                    continue
                filename = k + '.json'
                jobs.append(gevent.spawn(put_attachment_loop, request_id, int(doc[k]), filename))
    gevent.joinall(jobs)

prepare_basic_input()
