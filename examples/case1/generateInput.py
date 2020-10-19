import random
import json

x = random.randrange(0, 100)
if random.random() < 0.5:
    x = -x
y = random.randrange(0, 100)
if random.random() < 0.5:
    y = -y

d = {'x': x, 'y': y}
json_str = json.dumps(d)

print(json_str)