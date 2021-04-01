import uuid
from function_manager import FunctionManager

manager = FunctionManager("functions")
for _ in range(10):
    # manager.run(function_name, request_id, runtime, input:{"file1": {"type": "MEM"/"DB", "value": path/doc, "size": ...}, "file2": ...},
            # output:{"file1": {"type": "MEM"/"DB", "value": path/doc, "size": ...}, "file2": ...})
    # return {"file1": {"type": "MEM"/"DB", "value": path/doc}, "file2":...}
