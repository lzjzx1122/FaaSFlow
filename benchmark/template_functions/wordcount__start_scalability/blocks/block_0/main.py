import os
import time
scalability_dir = store.fetch_scalability_config()
assert scalability_dir is not None
scalability_dir = scalability_dir['dir']
fn = list(os.listdir(scalability_dir))
files = []
for fname in fn:
    with open(scalability_dir + fname, 'r') as f:
        data = f.read()
    files.append(data)
    # store.post('file', data)

# st = time.time()
for data in files:
    store.post('file', data)
# ed = time.time()
# store.post('save_db', {'st': st, 'ed': ed}, debug=True)

