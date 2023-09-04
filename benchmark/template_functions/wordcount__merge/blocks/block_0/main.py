import time

# st = time.time()
counts = store.fetch(['counts'])['counts']
# ed = time.time()
# store.post('fetch_db', {'st': st, 'ed': ed}, debug=True)
# merge
# st = time.time()
res = {}
for wc in counts:
    for w in wc:
        if w not in res:
            res[w] = wc[w]
        else:
            res[w] += wc[w]
# ed = time.time()
# store.post('compute', {'st': st, 'ed': ed}, debug=True)
# time.sleep(0.1)
store.post('res', len(res))
