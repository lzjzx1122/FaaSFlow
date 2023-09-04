import numpy as np
import os, json
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

model_file_path = '/proxy/resnet50_final_violence.h5'
model = load_model(model_file_path)
SIZE = (224, 224)

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


# inputs = store.fetch(['user_name', 'image_name'])
# user_name = inputs['user_name']
# image_name = inputs['image_name']

image_data = store.fetch(['img'])['img']
input_filepath = os.path.join(ENV_WORKDIR, 'input.png')
with open(input_filepath, 'wb') as f:
    f.write(image_data)

# evt = json.loads(event)
# user_name = evt['user_name']
# document_id = evt['document_id']
# image_name = evt['image_name']

# user_object = db[user_name]

# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,image_name)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,image_name,save_path = input_filepath)

img = image.load_img(input_filepath, target_size=SIZE)
input_x = image.img_to_array(img)
input_x = np.expand_dims(input_x, axis=0)
preds = model.predict(input_x)

# document = user_object[document_id]
# output_result = {}
illegal = False
if preds[0][0] > 0.95:
    illegal = True
illegal = False
    # output_result['illegal_flag'] = True
    # output_result['illegal_reason'] = 'illegal: Violence elements detected in the image!'
# output_result['violence_value'] = str(preds[0][0])
# user_object.save(document)
# store.put(output_result, {})
store.post('illegal', illegal)
# main('{"user_name":"user_2","document_id":"object_id_1","image_name":"test.jpg"}')
