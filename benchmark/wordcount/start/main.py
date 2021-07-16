from Store import Store
def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    fn = store.fetch(['files'])['files']
    store.put({'filename': fn}, {})