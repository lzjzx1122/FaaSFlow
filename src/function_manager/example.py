import uuid
import couchdb
from function_manager import FunctionManager

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = f'http://{username}:{password}@127.0.0.1:5984/'
db_name = 'results'
db_server = couchdb.Server(couchdb_url)
db_server.delete(db_name)
db = db_server.create(db_name)

manager = FunctionManager("functions")

for _ in range(10):
    function_name = 'utility'
    request_id = uuid.uuid4().hex

    # input
    doc = request_id + "_" + function_name + "_file1"
    db[doc] = {"key": "file1", "value": "fsdfkshfshj"}
    runtime = 1
    input = {"file1" : {"type": "DB", "value": doc}, "file2": {"type": "MEM", "value": "0d169826ba974399b70badc049470fed_utility_file3.json"}}

    # output
    output = {"file3": {"type": "DB", "size" : 100}, "file4": {"type": "MEM", "size": 200}}

    res = manager.run(function_name, request_id, runtime, input, output)
    print(res)