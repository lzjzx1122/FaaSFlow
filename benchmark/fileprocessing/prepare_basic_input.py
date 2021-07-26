from os import lseek
import couchdb
import json

def main(request_id, filename):
    couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
    db_server = couchdb.Server(couchdb_url)
    db = db_server['results']
    if request_id in db:
        db.delete(db[request_id])
    db[request_id] = {}
    db.put_attachment(db[request_id], json.dumps(filename), filename='filename.json')
# main('ac', 'sample.md')