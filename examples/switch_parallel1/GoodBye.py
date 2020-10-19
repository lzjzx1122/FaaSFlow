import json
import sys

json_data = json.loads(sys.argv[1])
input = str(json_data['input'])

d = {'Result': 'The result is ' + input + ', GoodBye!'}
json_str = json.dumps(d)

print(json_str)