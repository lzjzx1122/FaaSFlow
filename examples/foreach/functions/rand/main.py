import random
from Store import Store


def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)

    param = store.fetch(['count'])
    count = int(param['count'])
    split_keys = []
    res = {}
    for i in range(count):
        split_keys.append('a' + str(i))
        res['a' + str(i)] = random.randrange(0, 10)
    res['split_keys'] = split_keys
    store.put(res, {})
