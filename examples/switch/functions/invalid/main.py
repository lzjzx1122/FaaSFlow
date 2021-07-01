from Store import Store

def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    param = store.fetch(['input1', 'input2'])
    res = {'sqrt_result':  'invalid inputs input1 ' + str(param['input1']) + ' input2 ' + str(param['input2'])}
    store.put(res, {})
