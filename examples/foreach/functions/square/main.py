import random
from Store import Store


def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    param = store.fetch(['x'])
    foreach_key = param['x']
    param = store.fetch([foreach_key])
    x = int(param[foreach_key])
    new_key = foreach_key + '_result'
    res = {new_key: x * x}
    store.put(res, {})
