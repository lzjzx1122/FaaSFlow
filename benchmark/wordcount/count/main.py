import re
from Store import Store
def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    fn = store.fetch(['filename'])['filename']
    content = store.fetch([fn])

    # count
    res = {}
    for w in re.split(r'\W+', content):
        if w not in res:
            res[w] = 1
        else:
            res[w] += 1

    store.put({'wordcount_'+fn: res}, {})