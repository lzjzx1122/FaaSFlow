import time
import string
import random
from Store import Store

def main(function, request_id, runtime, input, output):
    store = Store(function)
    input_res = store.fetch(request_id, input)
    
    for k in input_res.keys():
        print(k)

    output_res = {}
    for (k, v) in output.items():
        #result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = v['size']))
        result = 'a' * v['size']
        output_res[k] = result
    
    time.sleep(runtime)
    
    store.put(request_id, output, output_res)
