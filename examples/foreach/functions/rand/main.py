import random
from Store import Store


def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)

    param = store.fetch(['count'])
    count = int(param['count'])
    split_keys = []
    for i in range(count):
        split_keys.append(i)
    rand_result = []
    for _ in range(count):
        rand_result.append(random.randrange(0, 10))
    res = {'rand_result': rand_result, 'split_keys': split_keys}
    store.put(res, {})
