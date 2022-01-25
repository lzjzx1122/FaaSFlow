import json
import os

def translator(workflow_name: str):
    ## parse json build flat_workflow.yaml
    f = open('../benchmark/generator/' + workflow_name + '/main_50.json')
    data = json.load(f)
    jobs = data['workflow']['jobs'] 
    yaml_data = {}
    functions = []
    global_inputs = {}

    ## name to lowercase
    for job in jobs:
        job['name'] = job['name'].lower()

    for job in jobs:
        function = {'name': job['name'], 'source': job['name'], 'runtime': 1, 'scale': 3, 'mem_usage': 0.25}
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
            for i in range(len(job['children'])):
                job['children'][i] = job['children'][i].lower()
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

    # f = open(workflow_name + '/flat_workflow.yaml', 'w', encoding = 'utf-8')
    # yaml.dump(yaml_data, f, sort_keys=False)

    ## build images
    for function in functions:
        print('------building image for function ' + function['name'] + '------')
        os.system('docker build --no-cache -t ' + workflow_name + '_' + function['name'] + ' ../benchmark/generator')

    ## build function_info.yaml
    # yaml_data2 = {'workflow': workflow_name, 'max_containers': 1}
    # images = []
    # for function in functions:
    #     images.append({'image': workflow_name + '_' + function['name'], 'name': function['name'], 'qos_requirement': 0.95, 'qos_time': 100})
    # yaml_data2['functions'] = images
    # f2 = open(workflow_name + '/function_info.yaml', 'w', encoding = 'utf-8')
    # yaml.dump(yaml_data2, f2, sort_keys=False)

if __name__ == '__main__':
    translator('cycles')
    translator('epigenomics')
    translator('genome')
    translator('soykb')