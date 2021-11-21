import time
from Store import Store
def main(workflow_name, function_name, request_id, runtime, input, output, to, keys):
    store = Store(workflow_name, function_name, request_id, input, output, to, keys)
    inp = store.fetch(['html', 'score'])
    # pretent to do some uploading
    time.sleep(1)