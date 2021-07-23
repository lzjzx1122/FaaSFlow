import os
import docker
import couchdb
import time
import redis

# content = 'a' * 104857600

couchdb_url = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
db_server = couchdb.Server(couchdb_url)
if 'workflow_latency' not in db_server:
    db_server.create('workflow_latency')
# results_db = db_server['results']
# results_db['test'] = {}
# start = time.time()
# results_db.put_attachment(results_db['test'], content, 'test.txt')
# end = time.time()
# print('latency: ', end - start)

# redis_db = redis.StrictRedis(host='172.17.0.1', port=6380, db=0)
# start = time.time()
# redis_db['bandwidth_test'] = content
# end = time.time()
# print('latency: ', end - start)
