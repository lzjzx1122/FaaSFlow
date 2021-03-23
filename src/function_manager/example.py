import uuid
from function_manager import FunctionManager

manager = FunctionManager("functions")
for _ in range(10):
    request_id = uuid.uuid4().hex
    manager.run("utility", request_id, {"runtime": 1, "output_size":10})