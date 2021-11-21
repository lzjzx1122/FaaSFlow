from Store import Store

store = Store(workflow_name, function_name, request_id, input, output, to, keys)

def main():
    # fn = store.fetch(['filename'])['filename']
    fn = 'sample.md'
    with open('/text/'+fn, 'r') as f:
        content = f.read()
    store.put({'file': content}, {})
