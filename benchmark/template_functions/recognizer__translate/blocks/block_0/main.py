from googletrans import Translator
import couchdb
import os, json
import time

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)
translator = Translator()
# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())

# def get_fileNameExt(filename):
#     (shortname, extension) = os.path.splitext(filename)
#     return shortname, extension


extracted_text = store.fetch(['text'])['text']
# translated_text = translator.translate(extracted_text, dest='en').text # can't connect to google...
translated_text = extracted_text
time.sleep(0.1)
store.post('translated_text', translated_text)

# evt = json.loads(event)
# user_name = evt['user_name']
# document_id = evt['document_id']
# extracted_text_filename = evt['extracted_text_filename']

# user_object = db[user_name]

# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,extracted_text_filename)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,extracted_text_filename,save_path = input_filepath)

# shortname, extension = get_fileNameExt(extracted_text_filename)
# extract_text_path = os.path.join(input_path,'translated_{}.txt'.format(shortname))
# if os.path.exists(extract_text_path):os.remove(extract_text_path)

# with open(input_filepath,"r") as f:
#     text_content = f.read()
# result = translator.translate(text_content, dest='en')
# with open(extract_text_path,'w', encoding='utf-8') as f:
#     f.write(result.text)
# active_storage('PUT', user_object,document_id,extracted_text_filename,extract_text_path,'application/octet')

# main('{"user_name":"user_2","document_id":"object_id_1","extracted_text_filename":"extract_test.txt"}')
