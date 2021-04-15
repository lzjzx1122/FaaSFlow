import time
import string
import random
from Store import Store

def main(runtime, input, output):
    store = Store()
    input_res = store.fetch(request_id, input)
   
    output_res = {}
    for (k, v) in output.items():
        #result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = v['size']))
        result = 'a' * v['size']
        output_res[k] = result
    
    time.sleep(runtime)
    
    store.put(request_id, output, output_res)
