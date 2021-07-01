import random
from Store import Store


def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    foreach_keys = store.fetch(['x'])['x']
    new_keys = []
    for k in foreach_keys:
        new_keys.append(k + '_result')
    items = store.fetch(new_keys)
    add_result = 0
    for k in items:
        add_result += int(items[k])
    res = {'add_result': add_result}
    store.put(res, {})
