import couchdb
import os

couchdb_url = 'http://admin:admin@127.0.0.1:5984/'
couch = couchdb.Server(couchdb_url)
db = couch['test']
f = db.get_attachment('list4', '5.txt', default='no attachment')
print(f)
