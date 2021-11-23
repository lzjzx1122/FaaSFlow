def main():
    # fn = store.fetch(['filename'])['filename']
    fn = 'sample.md'
    with open('/text/'+fn, 'r') as f:
        content = f.read()
    store.put({'file': content}, {})
