import json
import yaml
import sys
import string
import random

f = open('main.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 
arn = 'acs:fc:cn-hangzhou:1065690032410086:services/utility.LATEST/functions/utility2'
        
# initalize
wf = {'version': 'v1', 'type': 'flow', 'steps':[]}

def generateParallel(branches, name):
    return {'type': 'parallel', 'name': name, 'branches': branches}

def generateTask(job):
    inputMappings = []
    inputMappings.append({'target': 'runtime', 'source': job['runtime']})
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
wf['steps'].append(generateParallel(branches, 'myparallel'))

# rest functions: mapMerge, chr, pipeup
for rest in range(4):
    wf['steps'].append(generateTask(jobs[cnt]))
    cnt += 1

wf_f = open('wf2.yaml', 'w', encoding = 'utf-8')
yaml.dump(wf, wf_f, sort_keys = False)

