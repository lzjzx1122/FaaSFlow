from typing import List
import couchdb
import parse_yaml
import sys

sys.path.append('../../../config')
import config

workflow = []
db = couchdb.Server(config.COUCHDB_URL)
timedict = {}
mxdis = 0
ans = []

def pre(request_id):
    global timedict, mxdis, ans
    timedict = {}
    mxdis = 0
    ans = []
    for _id in db['workflow_latency']:
        doc = db['workflow_latency'][_id]
        if doc['request_id'] != request_id or doc['phase'] != 'all':
            continue
        timedict[doc['function_name']] = doc['time']

def dfs(name, dis, path: List):
    global mxdis, ans
    path.append(name)
    tmpdis = dis
    if name in timedict:
        tmpdis = dis + timedict[name]
    if tmpdis > mxdis:
        mxdis = tmpdis
        ans = list(path)
    for name in workflow.nodes[name].prev:
        dfs(name, tmpdis, path)
    path.pop()

def analyze(workflow_name, request_id):
    global workflow, timedict
    workflow = parse_yaml.parse(workflow_name)
    pre(request_id)
    for name, _ in workflow.nodes.items():
        if name in timedict:
            dfs(name, 0, [])
    return ans
