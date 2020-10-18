import random
import json

d = {'x': random.randrange(0, 100), 'y':random.randrange(0, 100)}
json_str = json.dumps(d)

print(json_str)