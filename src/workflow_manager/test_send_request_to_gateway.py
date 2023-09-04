from gevent import monkey

monkey.patch_all()
import time
import gevent

from request_info import RequestInfo
import requests

base_url = 'http://127.0.0.1:{}/{}'


def post_request(request_id):
    request_info = {'request_id': request_id,
                    'workflow_name': 'file_processing',
                    'input_datas': {'$USER.read_file_address': {'datatype': 'entity', 'val': '/text/sample.md'},
                                    '$USER.upload_address': {'datatype': 'entity', 'val': '127.0.0.1'}}}
    st = time.time()
    r = requests.post(base_url.format(7000, 'run'), json=request_info)
    ed = time.time()
    print(ed - st, r.json())


events = []
for i in range(3):
    events.append(gevent.spawn(post_request, 'request_' + str(i).rjust(3, '0')))
    gevent.sleep(1)
for e in events:
    e.join()
