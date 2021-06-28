import time
import string
import random
from Store import Store

def main(function_name, request_id, runtime, input, output, foreach_id):

    store = Store(function_name, request_id)
    input_res = store.fetch(input, foreach_id)
    
    for k in input_res.keys():
        print(k)

    output_res = {}
    for (k, v) in output.items():
        #result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = v['size']))
        result = 'a' * v['size']
        output_res[k] = result
    
    time.sleep(runtime)
    
    store.put(output, output_res, foreach_id)
