import json
import logging
import uuid

class BookHotelError(Exception):
  pass

def handler(event, context):
  evt = json.loads(event)
  txn_id = uuid.uuid4()
  result = evt['result']
  logger = logging.getLogger()

  if result == "failed":
    logger.info("Book hotel failed, transaction_id %s", txn_id)
    raise BookHotelError("Book hotel exception")
  logger.info("Book hotel succeeded, transaction_id %s" % txn_id)
  return '{"book_hotel":"success", "transaction_id": "%s"}' % txn_id