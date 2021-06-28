import random
from Store import Store


def main(function_name, request_id, runtime, input, output, foreach_id):
    store = Store(function_name, request_id)
    param = store.fetch(input, foreach_id)

    x = int(param['x'])
    res = {'square_result': x * x}

    store.put(output, res, foreach_id)
