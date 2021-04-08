import json
import yaml
import sys
import os
import random

workflow_name = './cycles'
utility = 'utility.py' # sys.argv[2]

f = open(workflow_name + '/main_7.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 

zero_in = []
zero_out = []
for job in jobs:
    if len(job['parents']) == 0:
        zero_in.append(job['name'])
    if len(job['children']) == 0:
        zero_out.append(job['name'])

yaml_data = {'type': 'workflow', 'start': None, 'end': None, 'nodes': []}
if len(zero_in) == 1:
    yaml_data['start'] = zero_in[0]
else:
    yaml_data['start'] = 'start_node'
    yaml_data['nodes'].append({'name': 'start_node', 'type': 'function', 'source': utility, \
                              'parameters': {'runtime': 0}, 'runtime': 0, 'next': zero_in})
if len(zero_out) == 1:
    yaml_data['end'] = zero_out[0]
else:
    yaml_data['end'] = 'end_node'
    yaml_data['nodes'].append({'name': 'end_node', 'type': 'function', 'source': utility, \
                               'parameters': {'runtime': 0}, 'runtime': 0})
    for job in jobs:
        if job['name'] in zero_out:
            job['children'].append('end_node')

names = []
for job in jobs:
    names.append(job['name'])
    runtime = random.randint(0, 5)
    job['runtime'] = runtime
    if len(job['children']) == 0:
        yaml_data['nodes'].append({'name': job['name'], 'type': 'function', 'source': utility, \
                                    'parameters': {'runtime': job['runtime'] }, \
                                    'runtime': job['runtime'], 'files': job['files']})
    else:
         yaml_data['nodes'].append({'name': job['name'], 'type': 'function', 'source': utility, \
                                     'parameters': {'runtime': job['runtime']}, \
                                     'runtime': job['runtime'], 'files': job['files'], 'next': job['children']})

yaml_data = {'main': yaml_data}
f = open(workflow_name + '/main_7.yaml', 'w', encoding = 'utf-8')
yaml.dump(yaml_data, f, sort_keys=False)

os.system('rm -rf ../../src/function_manager/functions')
os.system('mkdir ../../src/function_manager/functions')
yaml_data2 = {"functions": []}
for name in names:
    os.system('mkdir ../../src/function_manager/functions/' + name)
    os.system('cp ../../src/function_manager/utility.py ../../src/function_manager/functions/' + name + "/main.py")
    yaml_data2["functions"].append({'name': name, 'qos_time': 1, 'qos_requirement': 0.99, 'max_containers' : 10})
f = open('../../src/function_manager/functions/function_info.yaml', 'w', encoding = 'utf-8')
yaml.dump(yaml_data2, f, sort_keys=False)
