import os
import couchdb
import json

request_id = '123'
couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
files = [fn for fn in os.listdir('.') if fn.endswith('txt')]

db_server = couchdb.Server(couchdb_url)
db = db_server['results']
if request_id in db:
    db.delete(db[request_id])
db[request_id] = {}
db.put_attachment(db[request_id], json.dumps(files), 'files.json')
for fn in files:
    with open(fn, 'r') as f:
        db.put_attachment(db[request_id], f.read(), fn, 'text/plain')