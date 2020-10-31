import sys
import yaml
import queue
from ServerlessBase import ServerlessBase
from Function import Function
from Workflow import Workflow
from Switch import Switch

func_keys = {'type', 'next', 'parameters', 'source'}
switch_keys = {'type', 'next', 'choices'}
wf_keys = {'type', 'next', 'start', 'end', 'nodes'}
all_keys = {'type', 'next', 'start', 'end', 'parameters', 'source', 'choices', 'nodes', 'condition', 'go', 'default'}

def dataAtIndex(data, index):
    return data[index] if index in data else None 

# --------------------------------- Checking format errors begins. -------------------------------
def check(data, name):
    tp = dataAtIndex(data, 'type')
    # print("check:", name, tp)
    if tp == 'function':
        return checkFunction(data, name)
    elif tp == 'workflow':
        return checkWorkflow(data, name)
    elif tp == 'switch':
        return checkSwitch(data, name)
    else:
        raise Exception('The type of \'{}\' should be function, workflow or switch.'.format(name))

def checkFunction(data, name):
    if name in objectMap:
        raise Exception('\'{}\' should be defined once.'.format(name))
    objectMap[name] = None

    next = dataAtIndex(data, 'next')
    if next and type(next) is not str and type(next) is not list:
        raise Exception('The key \'next\' of \'{}\' should be a str or list.'.format(name))

    parameters = dataAtIndex(data, 'parameters')
    if parameters and type(parameters) is not dict:
        raise Exception('The key \'parameters\' of \'{}\' should be a dict.'.format(name))
    
    source = dataAtIndex(data, 'source')
    if source is None:
        raise Exception('The key \'source\' should be in \'{}\'.'.format(name))
    if type(source) is not str:
        raise Exception('The key \'source\' of \'{}\' should be a str.'.format(name))
    
    for key in all_keys:
        if key not in func_keys and dataAtIndex(data, key):
            raise Exception('The key \'{}\' should not be in \'{}\'.'.format(key, name))

def checkSwitch(data, name):
    if name in objectMap:
        raise Exception('\'{}\' should be defined once'.format(name))
    objectMap[name] = None

    next = dataAtIndex(data, 'next')
    if next and type(next) is not str and type(next) is not list:
        raise Exception('The key \'next\' of \'{}\' should be a str or list.'.format(name))
        
    choices = dataAtIndex(data, 'choices')
    if choices is None:
        raise Exception('The key \'choices\' should be in \'{}\'.'.format(name))
    elif type(choices) is not list:
        raise Exception('The key \'choices\' of \'{}\' should be a list.'.format(name))

    for choice in choices:
        if type(choice) is not dict:
            raise Exception('All choices of \'{}\' should be dict.'.format(name))
        if 'condition' in choice and 'go' in choice:
            if type(choice['go']) is dict:
                if 'name' not in choice['go']:
                    raise Exception('The key \'name\' should be in all choices of \'{}\''.format(name))
                check(choice['go'], choice['go']['name'])
            elif type(choice['go']) is not str:
                raise Exception('All choices of \'{}\' should be dict or str.'.format(name))
        elif 'default' in choice:
            if type(choice['default']) is dict:
                if 'name' not in choice['default']:
                    raise Exception('The key \'name\' should be in default choice of \'{}\''.format(name))
                check(choice['default'], choice['default']['name'])
            elif type(choice['default']) is not str:
                raise Exception('The default choice of \'{}\' should be a dict or str.'.format(name))
        else:
            raise Exception('Invalid choice appears in switch \'{}\''.format(name))

    for key in all_keys:
        if key not in switch_keys and dataAtIndex(data, key):
            raise Exception('The key \'{}\' should not be in \'{}\'.'.format(key, name))

def checkWorkflow(data, name):
    if name in objectMap:
        raise Exception('\'{}\' should be defined once'.format(name))
    objectMap[name] = None

    next = dataAtIndex(data, 'next')
    if next and type(next) is not str and type(next) is not list:
        raise Exception('The key \'next\' of \'{}\' should be a str or list.'.format(name))

    start = dataAtIndex(data, 'start')
    if start is None:
        raise Exception('The key \'start\' should be in \'{}\'.'.format(name))   
    if type(start) is not str:
        raise Exception('The key \'start\' of \'{}\' should be a str.'.format(name))    

    end = dataAtIndex(data, 'end')
    if end is None:
        raise Exception('The key \'end\' should be in \'{}\'.'.format(name))   
    if type(end) is not str:
        raise Exception('The key \'end\' of \'{}\' should be a str.'.format(name))       
    
    nodes = dataAtIndex(data, 'nodes')  
    if nodes is None:
        raise Exception('The key \'nodes\' should be in \'{}\'.'.format(name))
    if type(nodes) is not list:
        raise Exception('The key \'nodes\' should be a list.'.format(name))
    for node in nodes:
        if type(node) is dict:
            if 'name' not in node:
                raise Exception('The key \'name\' should be in all nodes of \'{}\''.format(name))
            check(node, node['name'])
        elif type(node) is not str:
            raise Exception('All nodes of \'{}\' should be str or dict.'.format(name))

    for key in all_keys:
        if key not in wf_keys and dataAtIndex(data, key):
            raise Exception('The key \'{}\' should not be in \'{}\'.'.format(key, name))
# --------------------------------- Checking format errors ends. ---------------------------------


# ------------------ Enumrate all Function/Switch/Workflow and transform them to objects. --------
def parse(data, name):
    tp = dataAtIndex(data, 'type')
    if tp == 'function':
        return parseFunction(data, name)
    elif tp == 'workflow':
        return parseWorkflow(data, name)
    elif tp == 'switch':
        return parseSwitch(data, name)
    
def parseFunction(data, name):
    parameters = dataAtIndex(data, 'parameters')
    source = dataAtIndex(data, 'source')
    next = dataAtIndex(data, 'next')
    if next is None:
        next = []
    elif type(next) is str:
        next = [next]
    res = Function(name, next, source, parameters)    
    objectMap[name] = res
    return res 

def parseSwitch(data, name):
    next = dataAtIndex(data, 'next')
    if next is None:
        next = []
    elif type(next) is str:
        next = [next]
      
    choices = dataAtIndex(data, 'choices')
    choices_str = {}
    for choice in choices:
        if 'condition' in choice and 'go' in choice:
            if type(choice['go']) is str:
                choices_str[choice['condition']] = choice['go']
            elif type(choice['go']) is dict:
                choices_str[choice['condition']] = choice['go']['name']
                parse(choice['go'], choice['go']['name'])
        elif 'default' in choice:
            if type(choice['default']) is str:
                choices_str['default'] = choice['default']
            elif type(choice['default']) is dict:
                choices_str['default'] = choice['default']['name']
                parse(choice['default'], choice['default']['name'])

    res = Switch(name, next, choices_str)
    objectMap[name] = res
    return res

def parseWorkflow(data, name):
    next = dataAtIndex(data, 'next')
    if next is None:
        next = []
    elif type(next) is str:
        next = [next]
   
    start = dataAtIndex(data, 'start')
    end = dataAtIndex(data, 'end')

    nodes = dataAtIndex(data, 'nodes')  
    nodes_str = []
    for node in nodes:
        if type(node) is str:
            nodes_str.append(node)
        elif type(node) is dict:
            nodes_str.append(node['name'])
            parse(node, node['name'])

    res =  Workflow(name, next, start, end, nodes_str)
    objectMap[name] = res
    return res
# ---------------------------------------- Enumrating Ends. -----------------------------------------

# ------------------------------------ Transform str to object. --------------------------------------
# Before the travel, obj.next = [str1, str2, str3]
# After the travel, obj.next = [obj1, obj2, obj3] 
def strToObj(obj):
    for k in range(len(obj.next)):
        nxt = objectMap[obj.next[k]]
        obj.next[k] = nxt
        nxt.prev.append(obj)
        nxt.prev_set.append(set())
        
    if type(obj) is Workflow:
        obj.start = objectMap[obj.start]
        obj.end = objectMap[obj.end]
        for k in range(len(obj.nodes)):
            node = objectMap[obj.nodes[k]]
            obj.nodes[k] = node
            node.father = obj
            strToObj(node)
    elif type(obj) is Switch:
        for (k,v) in obj.choices.items():
            choice = objectMap[v]
            obj.choices[k] = choice
            choice.father = obj
            strToObj(choice)
# ----------------------------------------- Transform end. ------------------------------------------


def check_next(obj):
    father = obj.father
    if type(father) is Switch and len(obj.next) > 0:
        raise Exception('Choice \'{}\' should not have the key \'next\'.'.format(obj.name))
    if type(father) is Workflow:
        for n in obj.next:
            if n not in father.nodes:
                raise Exception('\'{}\' can not point to \'{}\'.'.format(obj.name, n.name))
    
    if type(obj) is Workflow:
        for node in obj.nodes:
            check_next(node)
    elif type(obj) is Switch:
        for choice in obj.choices.values():
            check_next(choice)


# __name__ == '__main__'
filename = sys.argv[1] + 'main.yaml'
data = yaml.load(open(filename))
mainObject = None
objectMap = dict()    

# The first travel: check format errors.
if 'main' not in data:
    raise Exception('main not found.')
else:
    check(data['main'], 'main')
for name in data.keys():
    if name != 'main':
        check(data[name], name)

# The second travel: enumrate all Function/Switch/Workflow and transform them to objects.
mainObject = parse(data['main'], 'main')
for name in data.keys():
    if name != 'main':
        parse(data[name], name)

# The third travel.
strToObj(mainObject)

# Check whether the key 'next' is valid or not.
check_next(mainObject)

actions_yaml = {'max_container': 10, 'actions': []}
sources = set()
for obj in objectMap.values():
    if type(obj) is Function and obj.source not in sources:
        sources.add(obj.source)
        actions_yaml['actions'].append({'name': obj.source, 'pwd': obj.source, \
            'image': 'action_' + obj.source, 'qos_time': 100, 'qos_requirement': 0.95})
yaml.dump(actions_yaml, open(sys.argv[1] + 'actions.yaml', 'w'))
