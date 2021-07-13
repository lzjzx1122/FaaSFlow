import json
import yaml
import sys
import os
import random

workflow_name = './cycles'
utility = 'utility.py' # sys.argv[2]

## parse json build flat_workflow.yaml
f = open(workflow_name + '/main_50.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 

yaml_data = {}
functions = []
global_inputs = {}
for job in jobs:
    function = {'name': job['name'], 'source': job['name'], 'runtime': 1}
    inputs = {}
    outputs = {}
    for file in job['files']:
        name = file['name']
        size = file['size']
        if file['link'] == 'input':
            inputs[name] = {'type': 'pass', 'value': {'function': 'INPUT', 'parameter': name}, 'size': size}
        else:
            outputs[name] = {'type': 'normal', 'size': size}
    function['input'] = inputs
    function['output'] = outputs
    if 'children' in job:
        function['next'] = {'type': 'pass', 'nodes': job['children']}
    functions.append(function)
for function in functions:
    for name in function['input']:
        global_inputs[name] = function['input'][name]
for function in functions:
    for name in function['output']:
        if name in global_inputs:
            global_inputs.pop(name)
yaml_data['global_input'] = global_inputs
yaml_data['functions'] = functions

f = open(workflow_name + '/flat_workflow.yaml', 'w', encoding = 'utf-8')
yaml.dump(yaml_data, f, sort_keys=False)

## build functions and function_info.yaml

# names = []
# for node in yaml_data['main']['nodes']:
# 	names.append(node['name'])
# os.system('rm -rf ../../src/function_manager/functions')
# os.system('mkdir ../../src/function_manager/functions')
# yaml_data2 = {"functions": []}
# for name in names:
#     os.system('mkdir ../../src/function_manager/functions/' + name)
#     os.system('cp ../../src/function_manager/function_utility/main.py ../../src/function_manager/functions/' + name + "/main.py")
#     yaml_data2["functions"].append({'name': name, 'qos_time': 1, 'qos_requirement': 0.99, 'max_containers' : 10})
# f = open('../../src/function_manager/functions/function_info.yaml', 'w', encoding = 'utf-8')
# yaml.dump(yaml_data2, f, sort_keys=False)
