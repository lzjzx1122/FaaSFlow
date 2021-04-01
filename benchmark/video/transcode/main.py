# -*- coding: utf-8 -*-
import subprocess
import logging
import json
import os
import time

LOGGER = logging.getLogger()

class FFmpegError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status

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
def print_excute_time(func):
    def wrapper(*args, **kwargs):
        local_time = time.time()
        ret = func(*args, **kwargs)
        LOGGER.info('current Function [%s] excute time is %.2f' %
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
    # split video key, locate in nas
    input_path = evt['split_keys']
    fileDir, shortname, extension = get_fileNameExt(input_path)

    target_type = evt['target_type']
    transcoded_filename = 'transcoded_%s.%s' % (shortname, target_type)
    transcoded_filepath = os.path.join(fileDir, transcoded_filename)

    if os.path.exists(transcoded_filepath):
        os.remove(transcoded_filepath)

    exec_FFmpeg_cmd(['ffmpeg', '-y', '-i', input_path, transcoded_filepath])
    return {}

main('{"split_keys":"/home/openwhisk/Workflow/benchmark/video/1/split_output/split_test_piece_00.mp4", "target_type":"avi"}')