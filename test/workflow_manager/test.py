import time

import couchdb
import redis
import requests

from repository import Repository

# send request
req_id = '456'
repo = Repository()
start_functions = repo.get_start_functions()
print(start_functions)
for n in start_functions: # assume that there's only one start node
    info = repo.get_function_info(n, 'function_info')
    url = 'http://{}/request'.format(info['ip'])
    data = {
        'request_id': req_id,
        'workflow_name': 'test',
        'function_name': n,
        'no_parent_execution': True
    }
    start = time.time()
    requests.post(url, json=data)
    end = time.time()
latency = end - start
print(latency)

# get the result
# couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
# db_server = couchdb.Server(couchdb_url)
# db = db_server['results']
# r = db.get_attachment(db['123'], 'new_test.avi')
# with open('new_test.avi', 'wb') as f: f.write(r.read())
