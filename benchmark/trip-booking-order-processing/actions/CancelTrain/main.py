import random

def main(params):
  txn_id = params['txn_id']
  status = 0 if random.random() < 0.2 else 1
  return {'status': status, 'transaction_id': txn_id}