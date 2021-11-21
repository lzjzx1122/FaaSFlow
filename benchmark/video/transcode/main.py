# -*- coding: utf-8 -*-
import subprocess
import logging
import json
import os
import time
import couchdb
from Store import Store

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

LOGGER = logging.getLogger()
store = Store(workflow_name, function_name, request_id, input, output, to, keys)

class FFmpegError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status

# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())


def exec_FFmpeg_cmd(cmd_lst):
    try:
        subprocess.run(
            cmd_lst, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
    except subprocess.CalledProcessError as exc:
        LOGGER.error('returncode:{}'.format(exc.returncode))
        LOGGER.error('cmd:{}'.format(exc.cmd))
        LOGGER.error('output:{}'.format(exc.output))
        LOGGER.error('stderr:{}'.format(exc.stderr))
        LOGGER.error('stdout:{}'.format(exc.stdout))
        # log json to Log Service as db
        # or insert record in mysql, etc ...
        raise FFmpegError(exc.output, exc.returncode)

# a decorator for print the excute time of a function
# def print_excute_time(func):
#     def wrapper(*args, **kwargs):
#         local_time = time.time()
#         ret = func(*args, **kwargs)
#         LOGGER.info('current Function [%s] excute time is %.2f' %
#               (func.__name__, time.time() - local_time))
#         return ret
#     return wrapper

def get_fileNameExt(filename):
    (fileDir, tempfilename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(tempfilename)
    return fileDir, tempfilename, shortname, extension

# @print_excute_time
def main():
    # evt = json.loads(event)
    evt = store.fetch(['user_name', 'split_keys', 'target_type'])

    user_name = evt['user_name']
    # document_id = evt['document_id']
    split_keys = evt['split_keys']

    # user_object = db[user_name]
    fileDir, tempfilename, shortname, extension = get_fileNameExt(split_keys)
    # target_type = user_object[document_id]['target_type']
    target_type = evt['target_type']

    # input_path = os.path.join('..',user_name,document_id)
    # input_filepath = os.path.join(input_path,tempfilename)
    # if os.path.exists(input_filepath):os.remove(input_filepath)
    # else: os.makedirs(input_path)
    # active_storage('GET', user_object,document_id,tempfilename,save_path = input_filepath)

    input_filepath = tempfilename
    video = store.fetch([split_keys])[split_keys]
    with open(os.path.join('work', input_filepath), 'wb') as f: f.write(video)

    transcoded_filename = 'transcoded_%s.%s' % (shortname, target_type)
    # transcoded_path = os.path.join(input_path, 'transcode')
    # transcoded_filepath = os.path.join(transcoded_path,transcoded_filename)
    # if os.path.exists(transcoded_filepath):os.remove(transcoded_filepath)
    # else: os.makedirs(transcoded_path)
    transcoded_filepath = transcoded_filename

    exec_FFmpeg_cmd(['ffmpeg -y -i work/' + input_filepath + ' work/' + transcoded_filepath])
    # active_storage('PUT', user_object,document_id,transcoded_filename,transcoded_filepath,'application/octet')

    with open(os.path.join('work', transcoded_filepath), 'rb') as f: transcoded_video = f.read()
    store.put({transcoded_filename: transcoded_video}, {transcoded_filename: 'application/octet'})
    return {}

# main('{"user_name":"user_1","document_id":"object_id_3","split_keys":"../user_1/object_id_3/split_output/split_test_piece_13.mp4"}')