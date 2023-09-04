# -*- coding: utf-8 -*-
import subprocess
import logging
import os
import math

# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

MAX_SPLIT_NUM = 4
LOGGER = logging.getLogger()

# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())


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

# def print_excute_time(func):
#     def wrapper(*args, **kwargs):
#         local_time = time.time()
#         ret = func(*args, **kwargs)
#         LOGGER.info('current Function [%s] excute time is %.2f' %
#               (func.__name__, time.time() - local_time))
#         return ret
#     return wrapper

def get_fileNameExt(filename):
    (shortname, extension) = os.path.splitext(filename)
    return shortname, extension

def getVideoDuration(input_video):
    #cmd = '{0} -i {1} -show_entries format=duration -v quiet -of csv="p=0"'.format(FFPROBE_BIN, input_video)
    cmd = 'ffprobe -i work/'+input_video+' -show_entries format=duration -v quiet -of csv="p=0"'
    raw_result = subprocess.check_output(cmd, shell=True)
    result = raw_result.decode().replace("\n", "").strip()
    duration = float(result)
    return duration

# @print_excute_time

# evt = json.loads(event)
# evt = store.fetch(['user_name', 'video_name', 'segment_time'])
evt = store.fetch(['video_name', 'segment_time'])

# user_name = evt['user_name']
# document_id = evt['document_id']
video_name = evt['video_name']

# user_object = db[user_name]
# segment_time_seconds = str(user_object[document_id]['segment_time'])
segment_time_seconds = evt['segment_time']

shortname, extension = get_fileNameExt(video_name)

# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,video_name)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,video_name,save_path = input_filepath)

video = store.fetch(['video'])['video']
with open(os.path.join('work', video_name), 'wb') as f: f.write(video)

# video_proc_dir = os.path.join(input_path,'split_output')
video_proc_dir = 'split_output'
# if os.path.isdir(video_proc_dir) == False:
#     os.makedirs(video_proc_dir)
#     os.system("chmod -R 777 " + video_proc_dir)
os.mkdir(os.path.join('work', video_proc_dir))

input_filepath = video_name

video_duration = getVideoDuration(input_filepath)
segment_time_seconds = int(segment_time_seconds)
split_num = math.ceil(video_duration/segment_time_seconds)
# adjust segment_time_seconds
if split_num > MAX_SPLIT_NUM:
    segment_time_seconds = int(math.ceil(video_duration/MAX_SPLIT_NUM)) + 1

segment_time_seconds = str(segment_time_seconds)

command = 'ffmpeg -i work/'+ input_filepath + ' -c copy -f segment -segment_time ' + segment_time_seconds + " -reset_timestamps 1 work/" + video_proc_dir + "/split_"+ shortname + '_piece_%02d' + extension
exec_FFmpeg_cmd([command])

split_keys = []
for filename in os.listdir(os.path.join('work', video_proc_dir)):
    if filename.startswith('split_' + shortname):
        filekey = os.path.join(video_proc_dir, filename)
        with open(os.path.join('work', filekey), 'rb') as f: splited_video = f.read()
        # active_storage('PUT', user_object,document_id,filename,filekey,'application/octet')
        store.post('splited_video', splited_video, datatype='octet')
        # store.put({filename: splited_video}, {filename: 'application/octet'})
        split_keys.append(filename)
# document = user_object[document_id]
# document['split_keys'] = split_keys
# user_object.save(document)
# store.put({'split_keys': split_keys}, {})
store.post('split_keys', split_keys)

# main('{"user_name":"user_1","document_id":"object_id_3","video_name":"test.mp4"}')
