# -*- coding: utf-8 -*-
import logging
import os
import time
import json


# a decorator for print the excute time of a function
def print_excute_time(func):
    def wrapper(*args, **kwargs):
        local_time = time.time()
        ret = func(*args, **kwargs)
        print('current Function [%s] excute time is %.2f' %
              (func.__name__, time.time() - local_time))
        return ret
    return wrapper
    
def get_fileNameExt(filename):
    (fileDir, tempfilename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(tempfilename)
    return fileDir, shortname, extension

@print_excute_time
def main(event):
    evt = json.loads(event)
    input_path = evt['video_key']
    fileDir, shortname, extension = get_fileNameExt(input_path)

    target_type = evt['target_type']
    transcoded_filename = 'transcoded_%s.%s' % (shortname, target_type)
    transcoded_filepath = os.path.join(fileDir, transcoded_filename)

    if os.path.exists(transcoded_filepath):
        os.remove(transcoded_filepath)

    command = 'ffmpeg -y -i {0} -preset superfast {1}'.format(
        input_path, transcoded_filepath)
    os.system(command)
    return {}

main('{"video_key":"/home/openwhisk/Workflow/benchmark/video/1/test.mp4", "target_type":"avi"}')