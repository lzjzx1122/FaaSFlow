import sys
import json

# print(sys.argv[1])
json_data = json.loads(sys.argv[1])
L = json_data['L']
R = json_data['R']

for i in range(L, R + 1):
    if i == R:
        print(i)
    else:
        print(i, end = ' ')