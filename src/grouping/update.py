from typing import Dict, List
from repository import Repository
import component
import config

def fetch_logs(workflow_name: str) -> Dict:
    repo = Repository(workflow_name, remove_old_db=False)
    finished_request = repo.fetch_finished_request_id(workflow_name)
    return {_id: repo.fetch_logs(workflow_name, _id) for _id in finished_request}

def remove_logs(workflow_name: str, ids: List[str]):
    repo = Repository(workflow_name, remove_old_db=False)
    for _id in ids:
        repo.remove_logs(_id)

def reset_nextdis(workflow: component.workflow):
    for _, node in workflow.nodes:
        for i in range(len(node.nextDis)):
            node.nextDis[i] = 0

def reshape_by_key(logs: Dict) -> Dict:
    key_log = {}
    for _id in logs:
        for log in logs:
            key = log['key']
            if key not in key_log:
                key_log[key] = {'size': [], 'put_functions': [], 'get_functions': []}
            action = log['action']
            function = log['function']
            size = log['size']
            if action == 'PUT':
                key_log[key]['put_functions'].append(function)
                key_log[key]['size'].append(size)
            elif action == 'GET':
                key_log[key]['get_functions'].append(function)
    return key_log

def get_tail_size(sizes: List[int]): # 99-ile
    if len(sizes) < 100:
        return sizes[-1]
    return sizes[-int(len(sizes) / 100)]

def update_edge(workflow: component.workflow, start_function: str, end_function: str, size: int):
    start_node = workflow.nodes[start_function]
    for i in range(len(start_node.next)):
        next_node_name = start_node.next[i]
        if next_node_name == end_function:
            start_node.nextDis[i] += size / config.NETWORK_BANDWIDTH

def update_workflow(workflow: component.workflow, key_log: Dict):
    for key in key_log:
        size = get_tail_size(key_log[key]['sizes'])
        for start_function in key_log[key]['put_functions']:
            for end_function in key_log[key]['get_functions']:
                update_edge(workflow, start_function, end_function, size)

def update(workflow: component.workflow):
    logs = fetch_logs(workflow.workflow_name)
    reset_nextdis(workflow)
    key_log = reshape_by_key(logs)
    update_workflow(workflow, key_log)
    remove_logs(workflow.workflow_name, logs.keys())
