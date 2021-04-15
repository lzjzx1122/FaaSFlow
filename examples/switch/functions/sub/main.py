from Store import Store

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    param = store.fetch(input)

    x = int(param['x'])
    y = int(param['y'])
    
    res = {'sub_result': x - y}
    store.put(output, res)

    