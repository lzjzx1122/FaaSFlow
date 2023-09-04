# -*- coding: utf-8 -*-
import subprocess
import logging
import os

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

LOGGER = logging.getLogger()


class FFmpegError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status


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
#         print('current Function [%s] excute time is %.2f' %
#               (func.__name__, time.time() - local_time))
#         return ret
#     return wrapper

# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())


def get_fileNameExt(filename):
    (shortname, extension) = os.path.splitext(filename)
    return shortname, extension


# @print_excute_time
evt = store.fetch(['user_name', 'video_name', 'target_type'])

# evt = json.loads(event)
user_name = evt['user_name']
# document_id = evt['document_id']
video_name = evt['video_name']

# user_object = db[user_name]
shortname, _ = get_fileNameExt(video_name)
# target_type = user_object[document_id]['target_type']
target_type = evt['target_type']

video = store.fetch(['video'])['video']
with open(os.path.join('work', video_name), 'wb') as f: f.write(video)

# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,video_name)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,video_name,save_path = input_filepath)

transcoded_filename = 'transcoded_%s.%s' % (shortname, target_type)
# transcoded_path = os.path.join(input_path, 'simple_transcode')
# transcoded_filepath = os.path.join(transcoded_path,transcoded_filename)
# if os.path.exists(transcoded_filepath):os.remove(transcoded_filepath)
# else: os.makedirs(transcoded_path)

command = 'ffmpeg -y -i {0} -preset superfast {1}'.format(
    os.path.join('work', video_name), os.path.join('work', transcoded_filename))
exec_FFmpeg_cmd(command)
# active_storage('PUT', user_object,document_id,transcoded_filename,transcoded_filepath,'application/octet')
with open(os.path.join('work', transcoded_filename), 'rb') as f: transcoded_video = f.read()

# output_result = {transcoded_filename: transcoded_video}
# output_content_type = {transcoded_filename: 'application/octet'}
store.post('transcoded_video', transcoded_video, datatype='octet')
# store.put(output_result, output_content_type)
# return {}

# main('{"user_name":"user_1","document_id":"object_id_3","video_name":"test.mp4"}')
