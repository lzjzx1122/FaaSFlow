import couchdb
import time

time.sleep(2)
db = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984')
# db.delete('workflow_latency')
db.create('workflow_latency')
# db.delete('results')
db.create('results')
# db.delete('log')
db.create('log')
