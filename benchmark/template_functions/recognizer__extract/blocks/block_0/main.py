import cv2 as cv2
import pytesseract
import os, json
import numpy as np
from PIL import Image
import sys
from sys import argv
import couchdb


# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

def get_string(img_path):
    # Read image with opencv
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.1, fy=0.1)
    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    # Write the image after apply opencv to do some ...
    output_path = os.path.join(ENV_WORKDIR, 'thres.png')
    cv2.imwrite(output_path, img)
    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(Image.open(output_path))
    # os.remove(output_path)

    return result


def get_fileNameExt(filename):
    (shortname, extension) = os.path.splitext(filename)
    return shortname, extension


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
# inputs = store.fetch(['user_name', 'image_name', 'output_prefix'])
# image_name = inputs['image_name']
# mosaic_prefix = inputs['output_prefix']
image_data = store.fetch(['img'])['img']

input_filepath = os.path.join(ENV_WORKDIR, 'input.png')
with open(input_filepath, 'wb') as f: f.write(image_data)
# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,image_name)
# shortname, extension = get_fileNameExt(image_name)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,image_name,save_path = input_filepath)

text = get_string(input_filepath)
# extract_dir = os.path.join(input_path,'extract_text')
# extract_filename = 'extract_{}.txt'.format(shortname)
# extract_text_path = os.path.join(extract_dir, extract_filename)
# if os.path.isdir(extract_dir) == False:
#     os.makedirs(extract_dir)
# extract_filename = 'extract_{}.txt'.format(shortname)
# store.put({'extracted_text': result}, {})
store.post('text', text)
# active_storage('PUT', user_object,document_id,extract_filename,extract_text_path,'text/plain')
# document = user_object[document_id]
# document['extracted_text_filename'] = extract_filename
# user_object.save(document)

# main('{"user_name":"user_2","document_id":"object_id_1","image_name":"test.jpg"}')