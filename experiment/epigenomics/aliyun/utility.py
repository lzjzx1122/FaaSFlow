import random
import string
import time
import json


def handler(event, context):
    evt = json.loads(event)
    function_name = evt['function_name']
    runtime = evt[function_name]['runtime']
    files = evt[function_name]['files']
    res = {}
    for f in files:
        if f['link'] == 'input':
            name = f['name']
            print(evt[name])
        else:
            name = f['name']
            size = f['size']
            result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = size))
            res[name] = result
    print(res)
    time.sleep(runtime)
    return res
    
# event = {'function_name':'app', 'input.txt':'fu', 'app':{'runtime': 5, 'files': [{'link':'input', 'name': 'input.txt', 'size': 10}]}}
# handler(json.dumps(event), {})

    