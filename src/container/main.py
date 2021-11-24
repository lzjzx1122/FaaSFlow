import time
import string
import random

def main():
    input_res = store.fetch(store.input.keys())
    for k in input_res.keys():
        print(k)
    output_res = {}
    for (k, v) in store.output.items():
        result = 'a' * v['size']
        output_res[k] = result
    time.sleep(store.runtime)
    store.put(output_res, {})
