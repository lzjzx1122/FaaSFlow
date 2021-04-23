import yaml
import os
import sys
from hierarchy import Pass
from hierarchy import Parallel
from hierarchy import Switch
from hierarchy import Foreach
from hierarchy import Function
from hierarchy import global_input
from hierarchy import all_functions
from hierarchy import deep_copy

# ------------------------- Checking validity of yaml data ------------------------
names = set()

def valueAtIndex(data, index):
    return data[index] if index in data else None

def checkBase(data):
    name = valueAtIndex(data, 'name')
    if name == None:
        raise Exception('The key \'name\' is expected in all structures.')
    if name in names:
        raise Exception('Duplicate name: \'{}\'.'.format(name))
    names.add(name)
        
    tp = valueAtIndex(data, 'type')
    if tp == None:
        raise Exception('The key \'type\' is expected in \'{}\'.'.format(name))    
    elif tp == 'pass':
        checkPass(data, name)
    elif tp == 'parallel':
        checkParallel(data, name)
    elif tp == 'switch':
        checkSwitch(data, name)
    elif tp == 'foreach':
        checkForeach(data, name)
    elif tp == 'function':
        checkFunction(data, name)
    else:
        raise Exception('The key \'type\' in \'{}\' is expected to be a pass, parallel, switch, foreach or function.'.format(name))    

def checkPass(data, name):
    steps = valueAtIndex(data, 'steps')
    if steps is None:
        raise Exception('The key \'stpes\' is expected in \'{}\'.'.format(name))
    if type(steps) is not list:
        raise Exception('The key \'stpes\' in \'{}\' is expected to be a list.'.format(name))
    for step in steps:
        if type(step) is dict:
            checkBase(step)
        else:
            raise Exception('All steps of \'{}\' are expected to be dicts.'.format(name))

def checkParallel(data, name):
    branches = valueAtIndex(data, 'branches')
    if branches is None:
        raise Exception('The key \'branches\' is expected in \'{}\'.'.format(name))
    if type(branches) is not list:
        raise Exception('The key \'branches\' in \'{}\' is expected to be a list.'.format(name))
    for branch in branches:
        if type(branch) is dict:
            checkBase(branch)
        else:
            raise Exception('All branches of \'{}\' are expected to be dicts.'.format(name))

def checkSwitch(data, name):
    choices = valueAtIndex(data, 'choices')
    if choices is None:
        raise Exception('The key \'choices\' is expected in \'{}\'.'.format(name))
    elif type(choices) is not list:
        raise Exception('The key \'choices\' in \'{}\' is expected to be a list.'.format(name))

    for choice in choices:
        if 'condition' in choice and 'go' in choice:
            if type(choice['condition']) is not str:
                raise Exception('All conditions of \'{}\' are expected to be strs.'.format(name))        
            if type(choice['go']) is dict:
                checkBase(choice['go'])
            else:
                raise Exception('All goes of \'{}\' are expected to be dicts.'.format(name))
        else:
            raise Exception('Invalid choice in \'{}\''.format(name))

def checkForeach(data, name):
    task = valueAtIndex(data, 'task')
    if task == None:
        raise Exception('The key \'task\' is expected in \'{}\'.'.format(name))    

    type = valueAtIndex(task, 'type')
    if type == None:
        raise Exception('The key \'type\' is expected in task of \'{}\'.'.format(name))    
    elif type != 'function':
        raise Exception('The key \'type\ in task of \'{}\' is expected to be a function.'.format(name))    
    
    checkBase(task)

def checkFunction(data, name):
    source = valueAtIndex(data, 'source')
    if source == None:
        raise Exception('The key \'resouce\' is expected in \'{}\'.'.format(name))    
    
    output = valueAtIndex(data, 'output')
    if output != None: 
        if type(output) is not list:
            raise Exception('The key \'output\' in \'{}\' is expected to be a list.'.format(name))        
        for output in output:
            if type(output) is not str:
                raise Exception('All values in \'output\' in \'{}\' is expected to be a str.'.format(name))            

# --------------------------------- Checking ends. ---------------------------------


# ----------------------- Parse yaml data to objects. ---------------------
def parseBase(data):
    tp = valueAtIndex(data, 'type')
    if tp == 'pass':
        return parsePass(data)
    elif tp == 'parallel':
        return parseParallel(data)
    elif tp == 'switch':
        return parseSwitch(data)
    elif tp == 'foreach':
        return parseForeach(data)
    elif tp == 'function':
        return parseFunction(data)

def parsePass(data):
    name = valueAtIndex(data, 'name')
    inputMappings = valueAtIndex(data, 'inputMappings')
    outputMappings = valueAtIndex(data, 'outputMappings')
    steps = valueAtIndex(data, 'steps')
    steps_obj = []
    for step in steps:
        steps_obj.append(parseBase(step))
    return Pass(name, inputMappings, outputMappings, steps_obj)

def parseParallel(data):
    name = valueAtIndex(data, 'name')
    inputMappings = valueAtIndex(data, 'inputMappings')
    outputMappings = valueAtIndex(data, 'outputMappings')
    branches = valueAtIndex(data, 'branches')
    branches_obj = []
    for branch in branches:
        branches_obj.append(parseBase(branch))
    return Parallel(name, inputMappings, outputMappings, branches_obj)
        
def parseSwitch(data):
    name = valueAtIndex(data, 'name')
    inputMappings = valueAtIndex(data, 'inputMappings')
    outputMappings = valueAtIndex(data, 'outputMappings')
    choices = valueAtIndex(data, 'choices')
    choices_obj = []
    for choice in choices:
        choices_obj.append({'condition': choice['condition'], 'go': parseBase(choice['go'])})
    return Switch(name, inputMappings, outputMappings, choices_obj)

def parseForeach(data):
    name = valueAtIndex(data, 'name')
    inputMappings = valueAtIndex(data, 'inputMappings')
    outputMappings = valueAtIndex(data, 'outputMappings')
    task = valueAtIndex(data, 'task')
    return Foreach(name, inputMappings, outputMappings, parseBase(task))

def parseFunction(data):
    name = valueAtIndex(data, 'name')
    inputMappings = valueAtIndex(data, 'inputMappings')
    outputMappings = valueAtIndex(data, 'outputMappings')
    source = valueAtIndex(data, 'source')
    output = valueAtIndex(data, 'output')
    return Function(name, inputMappings, outputMappings, source, output, False)
# ---------------------------- Parse ends. ----------------------------------

def fetch_global_input(path):
    for path, dir_list, file_list in os.walk(os.path.join(path, 'input')):  
        for file_name in file_list:  
            global_input[file_name] = {'type': 'pass', 'value': {'function': 'INPUT', 'parameter': file_name}}

def parse(path):
    filename = os.path.join(path, 'workflow.yaml')
    with open(filename, "r") as f:
        data = yaml.load(f) 
    checkBase(data)
    return parseBase(data)

def flatten_and_simplify(main):
    main.set_start_and_end()
    main.flatten()
    changed = True
    while changed:
        changed = False
        all_functions_ = []
        for i in range(len(all_functions)):
            current = all_functions[i]
            if current != None and current.is_virtual:
                if current.next['type'] == 'pass' and len(current.next['nodes']) == 1: 
                    next = current.next['nodes'][0]
                    if len(next.prev) == 1:
                    # case 1 for simplification
                    # The current virtual node has only one next node.
                        print('#remove:', current.name, next.name)
                        changed = True
                        current.is_removed = True
                        all_functions[i] = None
                        next.prev = []
                        for prev in current.prev:
                            next.prev.append(prev)
                            for j in range(len(prev.next['nodes'])):
                                if prev.next['nodes'][j] == current:
                                    prev.next['nodes'][j] = next
                elif len(current.next['nodes']) == 0: 
                # case 2 for simplification
                # The current virtual node has no next node.
                    print('#remove:', current.name)
                    changed = True
                    current.is_removed = True
                    all_functions[i] = None
                    for prev in current.prev:
                        prev.next['nodes'].remove(current)
                elif len(current.prev) == 1:
                    prev = current.prev[0]
                    if prev.next['type'] == 'pass' and len(prev.next['nodes']) == 1:
                    # case 3 for simplification
                    # The current virtual node has only one prev node, which has one next node.
                        print('#remove:', current.name)
                        changed = True
                        current.is_removed = True
                        all_functions[i] = None
                        prev.next = current.next
                        for next in current.next['nodes']:
                            assert len(next.prev) == 1
                            next.prev[0] = prev
                     

path = '../../examples/parallel'
# Step 1. Fetch all inputs from path.
fetch_global_input(path)

# Step 2. Parse workflow.yaml to a object with hierarchical struture.
main = parse(path)

# Step 3. Inference all input of functions and the global output.
global_output = main.get_output(deep_copy(global_input))
print('final:', global_output)

# Step 4. Flatten the hierarchical struture to a flat one by adding some virtual nodes.
#         Simplify the flat struture by removing some redundant virtual nodes.
flatten_and_simplify(main)

# Step 5. Print the flat struture. 
yaml_data = main.get_yaml()
yaml_data = {'global_input': global_input, 'fuctions': yaml_data, 'global_output': global_output}
with open(os.path.join(path, 'flat_workflow.yaml'), 'w', encoding = 'utf-8') as f:
    yaml.dump(yaml_data, f, sort_keys=False)