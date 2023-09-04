# -*- coding: utf-8 -*-
import subprocess
import logging
import json
import os
import sys
import time
import shutil
import couchdb

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

LOGGER = logging.getLogger()

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
            cmd_lst, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
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
#                     (func.__name__, time.time() - local_time))
#         return ret
#     return wrapper


def get_fileNameExt(filename):
    (fileDir, tempfilename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(tempfilename)
    return fileDir, filename, shortname, extension


# @print_excute_time

video_list = store.fetch(['video'])['video']


evt = store.fetch(['user_name', 'split_keys', 'target_type', 'output_prefix', 'video_name'])
# evt = json.loads(event)
user_name = evt['user_name']
# document_id = evt['document_id']
split_keys = evt['split_keys']
target_type = evt['target_type']
output_prefix = evt['output_prefix']
video_name = evt['video_name']


# user_object = db[user_name]
# video_key = user_object[document_id]['video_key']
# target_type = user_object[document_id]['target_type']
# output_prefix = user_object[document_id]['output_prefix']

transcoded_split_keys = []
# input_path = os.path.join('..',user_name,document_id)
# transcoded_input_path = os.path.join(input_path, 'split_output')
transcoded_input_path = os.path.join(ENV_WORKDIR, 'split_output')
os.mkdir(transcoded_input_path)
for k, video in enumerate(video_list):
    # fileDir, filename, shortname, extension = get_fileNameExt(k)
    transcoded_input_filename = 'transcoded_%s.%s' % (str(k), target_type)
    transcoded_input_filepath = os.path.join(transcoded_input_path, transcoded_input_filename)
    # if os.path.exists(transcoded_input_path) == False:
    #     os.makedirs(transcoded_input_path)
    # elif os.path.exists(transcoded_input_filename):
    #     os.remove(transcoded_input_filename)
    # active_storage('GET', user_object,document_id,transcoded_input_filename,save_path = transcoded_input_filepath)
    # video = store.fetch([transcoded_input_filename])[transcoded_input_filename]
    with open(transcoded_input_filepath, 'wb') as f: f.write(video)
    transcoded_split_keys.append(transcoded_input_filepath)

#creds = context.credentials
if len(transcoded_split_keys) == 0:
    raise Exception("no transcoded_split_keys")

LOGGER.info({
    "target_type": target_type,
    "transcoded_split_keys": transcoded_split_keys
})

fileDir1, filename1, shortname1, extension1 = get_fileNameExt(video_name)
# video_process_dir = os.path.join('/home/openwhisk/Workflow_runnable/Workflow/benchmark/video/', 'merge_output')
# video_process_dir = 'merge_output'
segs_filename = 'segs_%s.txt' % (shortname1 + target_type)
# segs_filepath = os.path.join(video_process_dir, segs_filename)
segs_filepath = os.path.join(ENV_WORKDIR, segs_filename)

# if os.path.exists(video_process_dir) == False:
#     os.makedirs(video_process_dir)
#     os.system("chmod -R 777 " + video_process_dir)
# if os.path.exists(segs_filepath):
#     os.remove(segs_filepath)
with open(segs_filepath, 'a+') as f:
    # transcoded_split_keys.sort(key=lambda x:int(x.split('transcoded_split_'+shortname1+'_piece_')[1].split('.'+target_type)[0]))
    for filepath in transcoded_split_keys:
        f.write("file '%s'\n" % filepath.split('/', 2)[2])

merged_filename = output_prefix + '_' + shortname1 + "." + target_type
# merged_filepath = os.path.join(video_process_dir, merged_filename)
merged_filepath = os.path.join(ENV_WORKDIR, merged_filename)
# if os.path.exists(merged_filepath):
#     os.remove(merged_filepath)

# exec_FFmpeg_cmd(['ffmpeg -f concat -safe 0 -i ' + segs_filepath + ' -c copy -fflags +genpts ' + merged_filepath])
os.system('ffmpeg -f concat -safe 0 -i ' + segs_filepath + ' -c copy -fflags +genpts ' + merged_filepath)

LOGGER.info('output_prefix ' + output_prefix)
LOGGER.info("Uploaded %s to %s" % (filename1, merged_filepath))
# time.sleep(0.5)
# with open(merged_filepath, 'rb') as f: merged_video = f.read()
# store.put({merged_filename: merged_video}, {merged_filename: 'application/octet'})
store.post('merged_video', 'ok')
# active_storage('PUT', user_object,document_id,merged_filename,merged_filepath,'application/octet')
# document = user_object[document_id]
# document['video_proc_dir'] = video_process_dir
# user_object.save(document)

# main('{"user_name":"user_1","document_id":"object_id_3","split_keys": ["../user_1/object_id_3/split_output/split_test_piece_13.avi","../user_1/object_id_3/split_output/split_test_piece_11.avi","../user_1/object_id_3/split_output/split_test_piece_12.avi"]}')