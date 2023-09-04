import cv2 as cv2
import couchdb
import os, json

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())


# evt = json.loads(event)
# user_name = evt['user_name']
# document_id = evt['document_id']
# image_name = evt['image_name']

# user_object = db[user_name]
# illegal_flag = user_object[document_id]['illegal_flag']
# inputs = store.fetch(['user_name', 'image_name', 'output_prefix'])
# image_name = inputs['image_name']
# mosaic_prefix = inputs['output_prefix']
image_data = store.fetch(['img'])['img']

input_filepath = os.path.join(ENV_WORKDIR, 'input.png')
with open(input_filepath, 'wb') as f:
    f.write(image_data)

# if illegal_flag == True:
# mosaic_prefix = user_object[document_id]['output_prefix']
# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,image_name)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,image_name,save_path = input_filepath)


img = cv2.imread(input_filepath, 1)
img = cv2.resize(img, None, fx=0.1, fy=0.1)
height, width, deep = img.shape
mosaic_height = 8
for m in range(height - mosaic_height):
    for n in range(width - mosaic_height):
        if m % mosaic_height == 0 and n % mosaic_height == 0:
            for i in range(mosaic_height):
                for j in range(mosaic_height):
                    b, g, r = img[m, n]
                    img[m + i, n + j] = (b, g, r)

mosaic_filename = 'output.jpg'
mosaic_filepath = os.path.join(ENV_WORKDIR, mosaic_filename)
# mosaic_path = os.path.join(input_path,'mosaic')
# mosaic_file_path = os.path.join(mosaic_path,mosaic_filename)
# if os.path.exists(mosaic_file_path):os.remove(mosaic_file_path)
# else: os.makedirs(mosaic_path)
cv2.imwrite(mosaic_filepath, img)

# active_storage('PUT', user_object,document_id,mosaic_filename,mosaic_file_path,'application/octet')
# else: pass
# with open(mosaic_filepath, 'rb') as f:
#     mosaic_img = f.read()
# store.put({'mosaic_name': mosaic_filename, mosaic_filename: mosaic_img}, {mosaic_filename: 'application/octet'})
store.post('content', 'ok')
# main('{"user_name":"user_2","document_id":"object_id_1","image_name":"test.jpg"}')
