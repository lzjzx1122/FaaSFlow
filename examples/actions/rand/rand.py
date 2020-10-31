import json
import random

d = {'RandomResult': random.randrange(0, 10)}
json_str = json.dumps(d)

print(json_str)