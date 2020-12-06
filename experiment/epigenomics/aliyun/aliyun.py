import json
import yaml
import sys
import string
import random

f = open('main.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 
arn = 'acs:fc:cn-hangzhou:1065690032410086:services/utility.LATEST/functions/utility'

# generate alias
alias_map = dict()
file_count = 0
for job in jobs:
    for f in job['files']:
        name = f['name']
        size = f['size']
        if name not in alias_map:
            alias = 'file' + str(file_count)
            alias_map[name] = alias
            f['name'] = alias
            file_count += 1
        else:
            f['name'] = alias_map[f['name']]

# normailize
size_map = dict()
size_sum = 0
for job in jobs:
    for f in job['files']:
        name = f['name']
        size = f['size']
        if name in size_map:
            size_map[name]['count'] += 1
        else:
            size_map[name] = {'size': size, 'count': 1}
            file_count += 1
            size_sum += size
for name in size_map.keys():
    size_map[name]['size'] = size_map[name]['size'] * 32768 // size_sum
for job in jobs:
    for f in job['files']:
        name = f['name']
        f['size'] = size_map[name]['size']
        
# initalize
wf = {'version': 'v1', 'type': 'flow', 'steps':[]}

def generateParallel(branches, name):
    return {'type': 'parallel', 'name': name, 'branches': branches}

def generateTask(job, first):
    inputMappings, outputMappings = [], []
    inputMappings.append({'target': 'runtime', 'source': job['runtime']})
    inputMappings.append({'target': 'files', 'source': job['files']})
    for f in job['files']:
        if f['link'] == 'input':
            if size_map[f['name']]['count'] == 1:
                tmp = ''.join(random.choices(string.ascii_lowercase + string.digits, k = f['size']))
                inputMappings.append({'target': f['name'], 'source': tmp})
            else:
                if first == True:
                    inputMappings.append({'target': f['name'], 'source': '$input.' + f['name']})
                else:
                    inputMappings.append({'target': f['name'], 'source': '$local.' + f['name']})
        else :
            outputMappings.append({'target': f['name'], 'source': '$local.' + f['name']})
    return {'type': 'task', 'name': job['name'], 'resourceArn': arn, 'inputMappings': inputMappings, 'outputMappings': outputMappings}
    
cnt = 0
# fastqSplit
wf['steps'].append(generateTask(jobs[cnt], first = True))
cnt += 1

# parallel
branches = []
for parallel in range(4):
    steps = [] 
    for step in range(4):
        steps.append(generateTask(jobs[cnt], first = (step == 0)))
        cnt += 1
    branches.append({'steps': steps})
wf['steps'].append(generateParallel(branches, 'myparallel'))

# rest functions: mapMerge, chr, pipeup
for rest in range(4):
    wf['steps'].append(generateTask(jobs[cnt], first = False))
    cnt += 1

wf_f = open('wf.yaml', 'w', encoding = 'utf-8')
yaml.dump(wf, wf_f, sort_keys = False)
