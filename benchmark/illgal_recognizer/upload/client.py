import requests
import os,time,json

file_path = '/home/openwhisk/Workflow_runnable/Workflow/benchmark/illegal_recoginzer/test.jpg'

def main(param):
    image_name = param['image_name']
    user_name = param['user_name']
    image_key = file_path
    request_id = param['request_id']
    url = 'http://10.2.64.8:10000/upload'
    data_json = {"image_name": image_name,"user_name": user_name,"image_key": image_key,"request_id":request_id}
    files = [
    ('document', (image_name, open(image_key, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data_json), 'application/json')),
    ]
    start_time = time.time()
    r = requests.post(url, files=files)
    latency = time.time()-start_time
    print(latency)
    return{"latency":latency}

main({"image_name":"test.jpg","user_name":"user_2","request_id":1})