import sys
import json
import math

json_data = json.loads(sys.argv[1])
x = int(json_data['x'])

d = {'Result': round(math.sqrt(x), 3)}
json_str = json.dumps(d)

print(json_str)