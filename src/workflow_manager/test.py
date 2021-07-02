import redis
import json
import couchdb
import os

couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
db_server = couchdb.Server(couchdb_url)
db = db_server['results']
r = db.get_attachment(db['123'], 'new_test.avi')
with open('new_test.avi', 'wb') as f: f.write(r.read())
