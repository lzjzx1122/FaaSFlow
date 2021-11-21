from Store import Store
def main(workflow_name, function_name, request_id, runtime, input, output, to, keys):
    store = Store(workflow_name, function_name, request_id, input, output, to, keys)
    # fn = store.fetch(['filename'])['filename']
    fn = 'sample.md'
    with open('/text/'+fn, 'r') as f:
        content = f.read()
    store.put({'file': content}, {})
