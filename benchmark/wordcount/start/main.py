import os
from Store import Store

store = Store(workflow_name, function_name, request_id, input, output, to, keys)

def main():
    fn = list(os.listdir('/text'))
    res = {'filename': fn}
    for fname in fn:
        with open('/text/'+fname, 'r') as f:
            res[fname] = f.read()
    store.put(res, {})
