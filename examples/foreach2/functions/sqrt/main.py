from Store import Store
import math

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    param = store.fetch(input)

    x = int(param['x'])
    
    res = {'sqrt_result':  round(math.sqrt(x), 3)}
    store.put(output, res)