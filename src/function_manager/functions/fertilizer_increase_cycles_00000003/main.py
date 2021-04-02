import time
import string
import random

def main(runtime, input, output):
    output_res = {}
    for (k, v) in output.items():
        result = ''.join(random.choices(string.ascii_lowercase + string.digits, k = v['size']))
        output_res[k] = result
    time.sleep(runtime)
    return output_res

# print(main({"runtime": 1, "output_size":10}))