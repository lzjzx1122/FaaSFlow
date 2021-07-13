import os
import docker
import couchdb

couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
db_server = couchdb.Server(couchdb_url)
results_db = db_server['results']
results_db.get_attachment(results_db['123'], 'a.txt')
