# -*- coding: utf-8 -*-
import subprocess
import logging
import json
import os
import time
import shutil

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
def main(event,context):
    evt = json.loads(event)
    video_key = evt['video_key']
    split_keys = evt['split_keys']
    output_prefix = evt['output_prefix']
    video_type = evt['target_type']
    video_process_dir = evt['video_proc_dir']

    transcoded_split_keys = []
    for k in split_keys:
        fileDir, shortname, extension = get_fileNameExt(k)
        transcoded_filename = 'transcoded_%s.%s' % (shortname, video_type)
        transcoded_filepath = os.path.join(fileDir, transcoded_filename)
        transcoded_split_keys.append(transcoded_filepath)

    #creds = context.credentials
    if len(transcoded_split_keys) == 0:
        raise Exception("no transcoded_split_keys")
    
    LOGGER.info({
        "target_type": video_type,
        "transcoded_split_keys": transcoded_split_keys
    })

    _, shortname, extension = get_fileNameExt(video_key)
    segs_filename = 'segs_%s.txt' % (shortname + video_type)
    segs_filepath = os.path.join(video_process_dir, segs_filename)

    if os.path.exists(segs_filepath):
        os.remove(segs_filepath)

    with open(segs_filepath, 'a+') as f:
        for filepath in transcoded_split_keys:
            f.write("file '%s'\n" % filepath)

    merged_filename = 'merged_' + shortname + "." + video_type
    merged_filepath = os.path.join(video_process_dir, merged_filename)

    if os.path.exists(merged_filepath):
        os.remove(merged_filepath)

    exec_FFmpeg_cmd(['ffmpeg', '-f', 'concat', '-safe', '0', '-i',
                     segs_filepath, '-c', 'copy', '-fflags', '+genpts', merged_filepath])

    LOGGER.info('output_prefix ' + output_prefix)
    merged_key = os.path.join(output_prefix, shortname, merged_filename)
    LOGGER.info("Uploaded %s to %s" % (merged_filepath, merged_key))
    res = {
        "video_type": merged_key,
        "video_proc_dir": video_process_dir
    }
    return res

main('{"split_keys": ["/home/openwhisk/Workflow/benchmark/video/1/split_output/split_test_piece_00.mp4", "/home/openwhisk/Workflow/benchmark/video/1/split_output/split_test_piece_01.mp4"], "video_proc_dir": "/home/openwhisk/Workflow/benchmark/video/1/split_output","video_key":"/home/openwhisk/Workflow/benchmark/video/1/test.mp4","output_prefix": "neo","target_type":"avi"}',1)