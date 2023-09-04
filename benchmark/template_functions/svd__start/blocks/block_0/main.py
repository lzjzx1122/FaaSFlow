import time
import numpy as np

# m = np.random.randint(0, 100, (16384, 1024))
# np.save('data.npy', m)
m = np.load('/proxy/data.npy')
res = np.split(m, 16, axis=0)

# data = res[0]
# st = time.time()
# U, Sigma, V = np.linalg.svd(data)
# ed = time.time()
# print(ed - st)
# st = time.time()
for data in res:
    store.post('matrix', data.dumps(), datatype='octet')
# store.post('save_db', {'st': st, 'ed': ed}, debug=True)

