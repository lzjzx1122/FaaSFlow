import time

import couchdb
import redis
import requests

from repository import Repository

# send request
req_id = '123'
repo = Repository()
start_nodes = repo.get_start_node_name()
for n in start_nodes: # assume that there's only one start node
    info = repo.get_function_info(n, 'function_info')
    url = 'http://{}/request'.format(info['ip'])
    data = {
        'request_id': req_id,
        'workflow_name': 'test',
        'function_name': n,
    }
    start = time.time()
    requests.post(url, json=data)
    end = time.time()
latency = end - start

# get the result
couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
db_server = couchdb.Server(couchdb_url)
db = db_server['results']
r = db.get_attachment(db['123'], 'new_test.avi')
with open('new_test.avi', 'wb') as f: f.write(r.read())
