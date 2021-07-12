from os import lseek
import couchdb
import json

def main(request_id, image_name, user_name):
    couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
    db_server = couchdb.Server(couchdb_url)
    db = db_server['results']
    if request_id in db:
        db.delete(db[request_id])
    db[request_id] = {}
    db.put_attachment(db[request_id], json.dumps(image_name), filename='image_name.json')
    db.put_attachment(db[request_id], json.dumps(user_name), filename='user_name.json')
    # here comes the image
    with open(image_name, 'rb') as f:
        db.put_attachment(db[request_id], f.read(), filename=image_name, content_type='application/octet')

main('456', "test.jpg", "ziliuziliu")