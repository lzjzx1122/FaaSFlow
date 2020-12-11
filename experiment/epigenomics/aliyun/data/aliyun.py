import json
import yaml
import sys
import string
import random

f = open('main.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 
arn = 'acs:fc:cn-hangzhou:1065690032410086:services/utility.LATEST/functions/utility4'

# initalize
wf = {'version': 'v1', 'type': 'flow', 'steps':[]}

# count
count_map = dict()
input = []
for job in jobs:
    for f in job['files']:
        name = f['name']
        size = f['size']
        if name not in count_map:
            count_map[name] = {"name": name, "count": 1, "size": size}
        else:
            count_map[name]["count"] += 1
for name in count_map.keys():
    if count_map[name]["count"] == 1:
        input.append(count_map[name])
input_f = open('input.json', 'w', encoding = 'utf-8')
json.dump(input, input_f, sort_keys = False, indent = 4)


def generateParallel(branches, name):
    return {'type': 'parallel', 'name': name, 'branches': branches}

def generateTask(job):
    inputMappings = []
    inputMappings.append({'target': 'runtime', 'source': job['runtime']})
    inputMappings.append({'target': 'files', 'source': job['files']})
    return {'type': 'task', 'name': job['name'], 'resourceArn': arn, 'inputMappings': inputMappings}
    
cnt = 0
# fastqSplit
wf['steps'].append(generateTask(jobs[cnt]))
cnt += 1

# parallel
branches = []
for parallel in range(4):
    steps = [] 
    for step in range(4):
        steps.append(generateTask(jobs[cnt]))
        cnt += 1
    branches.append({'steps': steps})
wf['steps'].append(generateParallel(branches, 'Parallel'))

# rest functions: mapMerge, chr, pipeup
for rest in range(4):
    wf['steps'].append(generateTask(jobs[cnt]))
    cnt += 1

wf_f = open('wf.yaml', 'w', encoding = 'utf-8')
yaml.dump(wf, wf_f, sort_keys = False)
