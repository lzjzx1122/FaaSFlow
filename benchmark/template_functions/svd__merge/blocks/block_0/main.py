import time
import numpy as np
import pickle

res = store.fetch(['res'])['res']
Y = np.concatenate([pickle.loads(data) for data in res], axis=0)
Sigma_Y = np.linalg.svd(Y, compute_uv=False)
store.post('res', 'ok')
