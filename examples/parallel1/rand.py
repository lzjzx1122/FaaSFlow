import json
import random

d = {'RandomNumber': random.randrange(0, 10)}
json_str = json.dumps(d)

print(json_str)