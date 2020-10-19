import sys
import json

json_data = json.loads(sys.argv[1])
x = int(json_data['x'])

d = {'Result': -x}
json_str = json.dumps(d)

print(json_str)