from os import lseek
import couchdb
import json

request_id = '123'
couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
db_server = couchdb.Server(couchdb_url)
db = db_server['results']
if request_id in db:
    db.delete(db[request_id])
db[request_id] = {}

filename = 'sample-01.md' # a file in start/text
db.put_attachment(db[request_id], json.dumps(filename), filename='filename.json')