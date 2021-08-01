from os import lseek
import couchdb
import json

def main(request_id, video_name, user_name, segment_time, target_type, split):
    print('----prepare input for ', request_id, '----')
    couchdb_url = 'http://openwhisk:openwhisk@172.17.0.1:5984/'
    db_server = couchdb.Server(couchdb_url)
    db = db_server['results']
    if request_id in db:
        db.delete(db[request_id])
    db[request_id] = {}
    db.put_attachment(db[request_id], json.dumps(video_name), filename='video_name.json')
    db.put_attachment(db[request_id], json.dumps(user_name), filename='user_name.json')
    db.put_attachment(db[request_id], json.dumps(segment_time), filename='segment_time.json')
    db.put_attachment(db[request_id], json.dumps(target_type), filename='target_type.json')
    db.put_attachment(db[request_id], json.dumps(split), filename='split.json')
    # here comes the video
    with open(video_name, 'rb') as f:
        db.put_attachment(db[request_id], f.read(), filename=video_name, content_type='application/octet')

# main('123', "sample.mp4", "ziliuziliu", 10, "avi", True)
