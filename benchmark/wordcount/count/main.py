import re

def main():
    fn = store.fetch(['filename'])['filename']
    content = store.fetch([fn])[fn]

    # count
    res = {}
    for w in re.split(r'\W+', content):
        if w not in res:
            res[w] = 1
        else:
            res[w] += 1

    store.put({'wordcount_'+fn: res}, {})