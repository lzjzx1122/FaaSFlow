import json
import yaml
import sys
import string
import random

f = open('main.json')
data = json.load(f)
jobs = data['workflow']['jobs'] 
arn = 'arn:aws:lambda:ap-northeast-2:768231020136:function:utility'
        
# initalize
wf = {'StartAt': jobs[0]['name'], "States":{}}

def generateTask(job, next_):
    parameters = {'runtime': job['runtime'], 'files': job['files']}
    if next_ == None:
        return {'Type': 'Task', 'Resource': arn, 'Parameters': parameters, 'End': True}
    else:
        return {'Type': 'Task', 'Resource': arn, 'Parameters': parameters, 'Next': next_}
    
cnt = 0
wf['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], 'Parallel')
cnt += 1

# parallel
branches = []
for parallel in range(4):
    branch = {'StartAt': jobs[cnt]['name'], 'States': {}} 
    for step in range(3):
        branch['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], jobs[cnt + 1]['name'])
        cnt += 1
    branch['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], None)
    cnt += 1
    branches.append(branch)
wf['States']['Parallel'] = {'Type': 'Parallel', 'Next': jobs[cnt]['name'], 'Branches': branches}

# rest functions: mapMerge, chr, pipeup
for rest in range(3):
    wf['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], jobs[cnt + 1]['name'])
    cnt += 1
wf['States'][jobs[cnt]['name']] = generateTask(jobs[cnt], None)
cnt += 1

wf_f = open('wf.json', 'w', encoding = 'utf-8')
json.dump(wf, wf_f, sort_keys = False, indent = 4)

