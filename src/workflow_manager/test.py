import requests
import json
r = requests.get('http://openwhisk:openwhisk@127.0.0.1:5984/results/123_fertilizer_increase_cycles_00000003')
result = json.loads(r.text)
print(result['duration'])
