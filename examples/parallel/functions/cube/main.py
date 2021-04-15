from Store import Store

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    param = store.fetch(input)

    x = param['x']
    res = {'cube_result': x * x * x}

    store.put(output, res)