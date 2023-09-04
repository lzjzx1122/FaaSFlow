import re
import time

content = store.fetch(['file'])['file']

# st = time.time()
# count
res = {}
for w in re.split(r'\W+', content):
    if w not in res:
        res[w] = 1
    else:
        res[w] += 1
# ed = time.time()
# store.post('compute', {'st': st, 'ed': ed}, debug=True)
store.post('res', res)
