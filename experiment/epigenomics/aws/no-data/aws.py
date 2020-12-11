import json
import yaml
import sys
import string
import random

f = open('main.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 
arn = 'arn:aws:lambda:ap-northeast-2:768231020136:function:utility2'
        
# initalize
wf = {'StartAt': jobs[0]['name'], "States":{}}
runtime = []

def generateTask(job, next_):
    parameters = {'runtime': job['runtime']}
    if next_ == None:
        return {'Type': 'Task', 'Resource': arn, 'Parameters': parameters, 'End': True}
    else:
        return {'Type': 'Task', 'Resource': arn, 'Parameters': parameters, 'Next': next_}
    
cnt = 0
wf['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], 'Parallel')
runtime.append(jobs[cnt]['runtime'])
cnt += 1

# parallel
branches = []
mx = 0
for parallel in range(4):
    tmp = 0
    branch = {'StartAt': jobs[cnt]['name'], 'States': {}} 
    for step in range(3):
        branch['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], jobs[cnt + 1]['name'])
        tmp += jobs[cnt]['runtime']
        cnt += 1
    branch['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], None)
    tmp += jobs[cnt]['runtime']
    cnt += 1
    if mx < tmp:
        mx = tmp
    branches.append(branch)
wf['States']['Parallel'] = {'Type': 'Parallel', 'Next': jobs[cnt]['name'], 'Branches': branches}
runtime.append(mx)
    
# rest functions: mapMerge, chr, pipeup
for rest in range(3):
    wf['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], jobs[cnt + 1]['name'])
    runtime.append(jobs[cnt]['runtime'])
    cnt += 1
wf['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], None)
runtime.append(jobs[cnt]['runtime'])
cnt += 1

print('runtime:', runtime, sum(runtime))
wf_f = open('wf.json', 'w', encoding = 'utf-8')
json.dump(wf, wf_f, sort_keys = False, indent = 4)

