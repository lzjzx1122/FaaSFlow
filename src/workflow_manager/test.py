import couchdb
import os
import json
import threading
import uuid

couchdb_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
couch = couchdb.Server(couchdb_url)
db = couch['results']

def put_to_db(k, content_type):
    print('k: ', k)
    if content_type == 'application/json':
        filename = k + '.json'
        print('filename: ', filename)
        db.put_attachment(db['124'], json.dumps(123),
                                filename=filename)

threads = []
for i in range(10):
    thread_ = threading.Thread(target=put_to_db, args=(str(i), 'application/json'))
    threads.append(thread_)
for thread_ in threads:
    thread_.start()
for thread_ in threads:
    thread_.join()
