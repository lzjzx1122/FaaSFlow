import json
import yaml
import sys

workflow_name = sys.argv[1]
utility = 'utility.py' # sys.argv[2]

f = open(workflow_name + '/main_500.json')
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

for job in jobs:
    if len(job['children']) == 0:
        yaml_data['nodes'].append({'name': job['name'], 'type': 'function', 'source': utility, \
                                    'parameters': {'runtime': job['runtime']}, \
                                    'runtime': job['runtime'], 'files': job['files']})
    else:
         yaml_data['nodes'].append({'name': job['name'], 'type': 'function', 'source': utility, \
                                     'parameters': {'runtime': job['runtime']}, \
                                     'runtime': job['runtime'], 'files': job['files'], 'next': job['children']})

yaml_data = {'main': yaml_data}
f = open(workflow_name + '/main_500.yaml', 'w', encoding = 'utf-8')
yaml.dump(yaml_data, f, sort_keys=False)