import time
from Store import Store

store = Store(workflow_name, function_name, request_id, input, output, to, keys)

def main():
    inp = store.fetch(['html', 'score'])
    # pretent to do some uploading
    time.sleep(1)