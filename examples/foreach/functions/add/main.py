import random
from Store import Store


def main(function_name, request_id, runtime, input, output, foreach_id):
    store = Store(function_name, request_id)
    param = store.fetch(input, foreach_id)

    x = param['x']
    add_result = 0
    for item in x:
        add_result += item
    res = {'add_result': add_result}

    store.put(output, res, foreach_id)
