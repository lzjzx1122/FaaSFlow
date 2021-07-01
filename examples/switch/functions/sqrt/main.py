from Store import Store
import math

def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    param = store.fetch(['x'])
    x = int(param['x'])
    res = {'sqrt_result':  round(math.sqrt(x), 3)}
    store.put(res, {})
