import couchdb
import os,json

couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
db = couchdb.Server(couchdb_address)

def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
    if avtive_type == 'PUT':
        content = open(file_path, 'rb')
        user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
        content.close()
    elif avtive_type == 'GET':
        r = user_object.get_attachment(document_id,filename = filename)
        with open(save_path,'wb') as f: f.write(r.read())

def get_fileNameExt(filename):
    (shortname, extension) = os.path.splitext(filename)
    return shortname, extension

def main(event):
    evt = json.loads(event)
    user_name = evt['user_name']
    video_name = evt['video_name']

    user_object = db[user_name]
    for id in user_object:
        if user_object[id]['video_name'] == video_name:
            preview_name = user_object[id]['preview_name']
            input_path = os.path.join('..',user_name,id,'preview_gif')
            input_filepath = os.path.join(input_path,preview_name)
            if os.path.exists(input_filepath):os.remove(input_filepath)
            else: os.makedirs(input_path)
            active_storage('GET', user_object,id,preview_name,save_path = input_filepath)
            break

main('{"user_name":"user_1","video_name":"test.mp4"}')
    