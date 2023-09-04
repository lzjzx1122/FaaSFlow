import json

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

# server = flask.Flask(__name__)

# def document_create_and_init(user_object, request_id, image_name, image_key):
#     new_doc_id = 'object_id_' + request_id
#     if user_object.get(new_doc_id) == None:
#         user_object[new_doc_id] = {
#             "image_name": image_name,
#             "image_key": image_key,
#             "output_prefix": "mosaic",
#             "violence_value": "",
#             "adult_value": "",
#             "extracted_text_filename": "",
#             "illegal_flag": False,
#             "illegal_reason": "",
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


# inputs = store.fetch(['image_name', 'user_name'])
image_path = '/proxy/test.png'
with open(image_path, 'rb') as f:
    img = f.read()
store.post('img', img, datatype='octet')
# print('OK')
# request_data = json.load(request.files['data'])
# request_file = request.files['document']
# request_store = {
#     "image_name": request_data['image_name'],
#     "user_name": request_data['user_name'],
#     "image_key": request_data['image_key'],
#     "request_id": str(request_data['request_id']),
#     "item": request_file
# }

# if request_store:
#     user_object = db[request_store['user_name']]
#     input_path = os.path.join('..',request_store['user_name'],'object_id_'+request_store['request_id'])
#     input_filepath = os.path.join(input_path,request_store['image_name'])
#     if os.path.exists(input_path) == False:
#         os.makedirs(input_path)
#     request_file.save(input_filepath)

#     new_doc_id = document_create_and_init(user_object, request_store['request_id'], request_store['image_name'], request_store['image_key'])

#     active_storage('PUT', user_object,new_doc_id,request_store['image_name'],input_filepath,'application/octet')

#     return '{"code": "ok"}'
# else:
#     return '{"message": "Please first upload a file!"}'

# server.run(port=10000, debug=True,host='0.0.0.0')
