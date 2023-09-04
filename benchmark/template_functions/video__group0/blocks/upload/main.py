import os


# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

# server = flask.Flask(__name__)

# def document_create_and_init(user_object, request_id, video_name, video_key, target_type, segment_time, preview_name):
#     new_doc_id = 'object_id_' + request_id
#     if user_object.get(new_doc_id) == None:
#         user_object[new_doc_id] = {
#             "video_name": video_name,
#             "split_keys": "",
#             "video_proc_dir": "",
#             "video_key": video_key,
#             "output_prefix": "new",
#             "target_type": target_type,
#             "segment_time": segment_time,
#             "preview_name": preview_name,
#         }
#     return new_doc_id

# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())
import shutil


def get_fileNameExt(filename):
    (shortname, extension) = os.path.splitext(filename)
    return shortname, extension


# def preview_generate(video_name, input_path,input_filepath):
#     output_path = os.path.join(input_path,'preview_gif')
#     shortname, extension = get_fileNameExt(video_name)
#     preview_filename = 'preview_'+shortname+'.gif' 
#     output_filepath = os.path.join(output_path,preview_filename)
#     if os.path.exists(output_filepath):os.remove(output_filepath)
#     else: os.makedirs(output_path)
#     command = 'ffmpeg -t 3 -ss 00:00:02 -i {0} {1}'.format(
#         input_filepath, output_filepath)
#     os.system(command)
#     return preview_filename, output_filepath

def preview_generate(video_name):
    # with open(os.path.join('work', video_name), 'wb') as f: f.write(video)
    shortname, _ = get_fileNameExt(video_name)
    preview_name = 'preview_' + shortname + '.gif'
    # command = 'ffmpeg -t 3 -ss 00:00:02 -i {0} {1}'.format(os.path.join('work', video_name), os.path.join('work', preview_name)) 
    command = 'ffmpeg -t 3 -ss 00:00:02 -i {0} {1}'.format(video_name, preview_name)
    os.system(command)
    # with open(os.path.join('work', preview_name), 'rb') as f: preview_video = f.read()
    with open(preview_name, 'rb') as f: preview_video = f.read()
    return preview_name, preview_video


# get method for downloading
# @server.route('/download', methods=['get'])
# def download():
#     fpath = request.values.get('path', '') #read file path
#     fname = request.values.get('filename', '')  #read file name
#     if fname.strip() and fpath.strip():
#         print(fname, fpath)
#         if os.path.isfile(os.path.join(fpath,fname)) and os.path.isdir(fpath):
#             return send_from_directory(fpath, fname, as_attachment=True) 
#         else:
#             return '{"message":"incorrect parameters!"}'
#     else:
#         return '{"message":"please input the parameters!"}'


# post method for uploading
# @server.route('/upload', methods=['post'])
# def main():
# print('OK')
# request_data = json.load(request.files['data'])
# request_file = request.files['document']
# request_store = {
#     "video_name": request_data['video_name'],
#     "user_name": request_data['user_name'],
#     "video_key": request_data['video_key'],
#     "target_type": request_data['target_type'],
#     "segment_time": request_data['segment_time'],
#     "request_id": str(request_data['request_id']),
#     "item": request_file
# }
# request_store = store.fetch(['video_name', 'user_name', 'target_type', 'segment_time'])

# if request_store:
# user_object = db[request_store['user_name']]
# input_path = os.path.join('..',request_store['user_name'],'object_id_'+request_store['request_id'])
# input_filepath = os.path.join(input_path,request_store['video_name'])
# if os.path.exists(input_path) == False:
#     os.makedirs(input_path)
# request_file.save(input_filepath)
# video_name = request_store['video_name']
# video = store.fetch([video_name])[video_name]
# preview_filename, output_filepath = preview_generate(request_store['video_name'],input_path,input_filepath)
# Todo: we need to add copy behavior in FaasFlow benchmark
if os.path.exists('test.mp4'):
    os.remove('test.mp4')
shutil.copy('/proxy/test.mp4', 'test.mp4')
video_name = 'test.mp4'
with open(video_name, 'rb') as f: video = f.read()
preview_name, preview_video = preview_generate(video_name)
# new_doc_id = document_create_and_init(user_object, request_store['request_id'], request_store['video_name'], request_store['video_key'], request_store['target_type'], request_store['segment_time'], preview_filename)

# active_storage('PUT', user_object,new_doc_id,request_store['video_name'],input_filepath,'application/octet')
# active_storage('PUT', user_object,new_doc_id,preview_filename,output_filepath,'image/gif')
output_result = {'output_prefix': 'new', 'preview_name': preview_name, preview_name: preview_video}
output_content_type = {preview_name: 'application/octet'}
store.post('output_prefix', 'new')
store.post('preview_name', preview_name)
store.post(preview_name, preview_video, datatype='octet')
# store.put(output_result, output_content_type)
store.post('video', video, datatype='octet')
# store.put({video_name: video}, {video_name: 'application/octet'})
store.post('video_name', video_name)
store.post('user_name', 'Barrin')
store.post('segment_time', 9)
store.post('target_type', 'avi')
store.post('split', True)
# store.put(
#     {'video_name': video_name, 'user_name': 'ziliuziliu', 'segment_time': 25, 'target_type': 'avi', 'split': True},
#     {})
# return '{"code": "ok"}'
# else:
#     return '{"message": "Please first upload a file!"}'

# server.run(port=10000, debug=True,host='0.0.0.0')
