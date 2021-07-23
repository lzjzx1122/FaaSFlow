from Store import Store
def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    fn = store.fetch(['filename'])['filename']
    with open('/text/'+fn, 'r') as f:
        content = f.read()
    store.put({'file': content}, {})
