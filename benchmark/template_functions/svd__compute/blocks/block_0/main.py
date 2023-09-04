import time
import numpy as np
import pickle

m = store.fetch(['matrix'])['matrix']
m = pickle.loads(m)
U, Sigma, VT = np.linalg.svd(m)
# data = res[0]
# st = time.time()
# U, Sigma, V = np.linalg.svd(data)
# ed = time.time()
# print(ed - st)
# st = time.time()
# store.post('res', {'U': base64.b64encode(U.dumps()).decode(), 'D_dot_VT': base64.b64encode(D_dot_VT.dumps()).decode()})
store.post('res', np.dot(np.diag(Sigma), VT).dumps(), datatype='octet')
# store.post('save_db', {'st': st, 'ed': ed}, debug=True)

