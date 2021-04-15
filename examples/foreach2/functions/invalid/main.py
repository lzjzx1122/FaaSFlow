from Store import Store

def main(function_name, request_id, runtime, input, output):
    store = Store(function_name, request_id)
    # param = store.fetch(input)

    res = {'sqrt_result':  "invalid"}
    store.put(output, res)