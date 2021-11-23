def main():
    fn = store.fetch(['filename'])['filename']
    keys = ['wordcount_'+f for f in fn]
    counts = store.fetch(keys)

    # merge
    res = {}
    for wc in counts.values():
        for w in wc:
            if w not in res:
                res[w] = wc[w]
            else:
                res[w] += wc[w]

    store.put({'result': res}, {})