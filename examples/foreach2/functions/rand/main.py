import random
from Store import Store

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    param = store.fetch(input)

    count = int(param['count'])
    
    array1 = []
    for _ in range(count):
        array1.append(random.randrange(0, 10))
    array2 = []
    for _ in range(count):
        array2.append(random.randrange(0, 10))

    res = {'rand_result1': array1, 'rand_result2': array2}
    
    store.put(output, res)