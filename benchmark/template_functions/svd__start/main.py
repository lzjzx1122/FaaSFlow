import time
import numpy as np
import os

m = np.random.randint(0, 100, (8192, 512))
np.save('data.npy', m)
# m = np.load('/proxy/data.npy')
# res = np.split(m, 16, axis=0)

# data = res[0]
# st = time.time()
st = time.time()
# U, Sigma, V = np.linalg.svd(m)
Sigma = np.linalg.svd(m, compute_uv=False)
ed = time.time()
print(ed - st)
# ed = time.time()
# print(ed - st)
# st = time.time()
# for data in res:
#     store.post('matrix', data.dumps(), datatype='octet')
# store.post('save_db', {'st': st, 'ed': ed}, debug=True)

