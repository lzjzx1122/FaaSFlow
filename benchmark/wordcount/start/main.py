import os
from Store import Store
def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    fn = list(os.listdir('/text'))
    res = {'filename': fn}
    for f in fn:
        with open('/text/'+f, 'r') as f:
            res[f] = f.read()
    store.put(res, {f:'text/plain' for f in fn})