import requests
import os,time,json

file_path = '/home/openwhisk/Workflow_runnable/Workflow/benchmark/video/test.mp4'

def main(param):
    video_name = param['video_name']
    user_name = param['user_name']
    segment_time = param['segment_time']
    video_key = file_path
    target_type = param['target_type']
    request_id = param['request_id']
    url = 'http://10.2.64.8:10000/upload'
    data_json = {"video_name": video_name,"user_name": user_name,"video_key": video_key,"segment_time": segment_time,"target_type":target_type,"request_id":request_id}
    files = [
    ('document', (video_name, open(video_key, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data_json), 'application/json')),
    ]
    start_time = time.time()
    r = requests.post(url, files=files)
    latency = time.time()-start_time
    print(latency)
    return{"latency":latency}

main({"video_name":"test.mp4","user_name":"user_1","segment_time":10,"target_type":"avi","request_id":3})