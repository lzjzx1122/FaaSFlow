import uuid
from function_manager import FunctionManager

manager = FunctionManager("functions")
for _ in range(10):
    request_id = uuid.uuid4().hex
    manager.run("utility", request_id, 1, {"runtime": 1, "output_size":10})
    # run(function_name, request_id, runtime, input:{"file1": [MEM, path] / [DB, doc_name], "file2":... })
    # return {"file1": [MEM, path] / [DB, doc_name], "file2":...}
