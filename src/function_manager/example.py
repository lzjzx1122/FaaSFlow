import uuidx`
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

for _ in range(1):
    function_name = 'utility'
    request_id = "123344"

    # input
    doc = request_id + "_" + function_name + "_file1"
    runtime = 1
    input = {"file1" : {"type": "MEM"}, "file2": {"type": "MEM"}}

    # output
    output = {"file3": {"type": "DB+MEM", "size" : 100}, "file4": {"type": "DB+MEM", "size": 200}}

    res = manager.run(function_name, request_id, runtime, input, output)
    print(res)
