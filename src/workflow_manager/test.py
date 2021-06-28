import couchdb

couchdb_url = 'http://admin:admin@127.0.0.1:5984/'
couch = couchdb.Server(couchdb_url)
db = couch['test']
r = db.get_attachment(db['list4'], '3.txt')
print(r)