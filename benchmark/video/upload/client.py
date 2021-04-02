import requests
import os,time,json

def main(param):
    file_name = param['name']
    request_id = param['request_id']
    url = 'http://10.2.64.8:10000/upload'
    data_json = {"file_name": file_name,"request_id":request_id}
    files = [
    ('document', (file_name, open("../1/"+file_name, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data_json), 'application/json')),
    ]
    start_time = time.time()
    r = requests.post(url, files=files)
    latency = time.time()-start_time
    print(latency)
    return{"latency":latency}

main({"name":"test.mp4","request_id":3})