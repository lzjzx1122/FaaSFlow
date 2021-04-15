import random
from Store import Store

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    # param = store.fetch(input)

    res = {'rand_result': random.randrange(0, 10)}
    
    store.put(output, res)