import time
import string
import random

def main(param):
    runtime = param['runtime']
    output_size = param['output_size']
    result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = output_size))
    time.sleep(runtime)
    return {"result": result}

# print(main({"runtime": 1, "output_size":10}))