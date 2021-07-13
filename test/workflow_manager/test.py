import time

import couchdb
import redis
import requests
import gevent
from gevent import monkey
monkey.patch_all()

from repository import Repository

# send request
req_id = '456'
repo = Repository()
start_functions = repo.get_start_functions()
print(start_functions)

def trigger_function(function_name):
    print('----triggering function ' + function_name + '----')
    info = repo.get_function_info(function_name, 'function_info')
    url = 'http://{}/request'.format(info['ip'])
    data = {
        'request_id': req_id,
        'workflow_name': 'test',
        'function_name': function_name,
        'no_parent_execution': True
    }
    requests.post(url, json=data)

jobs = []
start = time.time()
for n in start_functions: # assume that there's only one start node
    jobs.append(gevent.spawn(trigger_function, n))
gevent.joinall(jobs)
end = time.time()
latency = end - start
print(latency)

# get the result
# couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
# db_server = couchdb.Server(couchdb_url)
# db = db_server['results']
# r = db.get_attachment(db['123'], 'new_test.avi')
# with open('new_test.avi', 'wb') as f: f.write(r.read())
