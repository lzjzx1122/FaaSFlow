import random
import uuid

def main(params):
  txn_id = uuid.uuid4()
  status = 0 if random.random() < 0.2 else 1
  return {'status': status, 'transaction_id': '%s' % txn_id}