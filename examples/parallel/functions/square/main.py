import random
from Store import Store

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    param = store.fetch(input)

    x = int(param['x'])
    res = {'square_result': x * x}

    store.put(output, res)