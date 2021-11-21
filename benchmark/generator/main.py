import time
import string
import random
from Store import Store


def main(workflow_name, function_name, request_id, runtime, input, output, to, keys):
    store = Store(workflow_name, function_name, request_id, input, output, to, keys)
    input_res = store.fetch(input.keys())
    for k in input_res.keys():
        print(k)
    output_res = {}
    for (k, v) in output.items():
        result = 'a' * v['size']
        output_res[k] = result
    time.sleep(runtime)
    store.put(output_res, {})
