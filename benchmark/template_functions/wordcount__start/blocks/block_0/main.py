import os
import time

fn = list(os.listdir('/text'))
files = []
for fname in fn:
    with open('/text/' + fname, 'r') as f:
        data = f.read()
    files.append(data)
    # store.post('file', data)

# st = time.time()
for data in files:
    store.post('file', data)
# ed = time.time()
# store.post('save_db', {'st': st, 'ed': ed}, debug=True)

