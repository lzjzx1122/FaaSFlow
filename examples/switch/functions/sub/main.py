from Store import Store

def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    param = store.fetch(['x', 'y'])
    x = int(param['x'])
    y = int(param['y'])
    res = {'sub_result': x - y}
    store.put(res, {})


    