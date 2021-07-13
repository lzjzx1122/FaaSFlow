from base64 import urlsafe_b64decode
from os import execl
import time
import sys
import repository
import gevent
import gevent.lock
from typing import Any, Dict, List
import requests

sys.path.append('../function_manager')
from function_manager import FunctionManager

repo = repository.Repository()
class FakeFunc:
    def __init__(self, req_id: str, func_name: str):
        self.req_id = req_id
        self.func = func_name

    def __getattr__(self, name: str):
        return repo.fetch(self.req_id, name)


def cond_exec(req_id: str, cond: str) -> Any:
    if cond.startswith('default'):
        return True

    values = {}
    res = None
    while True:
        try:
            res = eval(cond, values)
            break
        except NameError as e:
            name = str(e).split("'")[1]
            values[name] = FakeFunc(req_id, name)

    return res

class WorkflowState:
    def __init__(self, request_id: str, all_func: List[str]):
        self.request_id = request_id
        self.lock = gevent.lock.BoundedSemaphore() # guard the whole state

        self.executed: Dict[str, bool] = {}
        self.parent_executed: Dict[str, int] = {}
        for f in all_func:
            self.executed[f] = False
            self.parent_executed[f] = 0

    def set_state(self, executed, parent_executed):
        self.executed = executed
        self.parent_executed = parent_executed

function_manager = FunctionManager("../../benchmark/generator/soykb") # demonstrate workflow definition(computation graph, code...)

# mode: 'optimized' vs 'normal'
class WorkflowManager:
    def __init__(self, host_addr: str, workflow_name: str, mode):
        self.lock = gevent.lock.BoundedSemaphore() # guard self.states
        self.host_addr = host_addr
        self.workflow_name = workflow_name
        self.states: Dict[str, WorkflowState] = {}
        self.function_info: Dict[str, dict] = {}

        self.foreach_func = repo.get_foreach_functions()
        self.merge_func = repo.get_merge_functions()
        
        self.mode = mode
        if mode == 'optimized':
            self.meta_db = 'function_info'
        else:
            self.meta_db = 'function_info_raw'
        self.func = repo.get_all_functions(self.meta_db) # get all the functions *run on this host*

    # return the workflow state of the request
    def get_state(self, request_id: str) -> WorkflowState:
        self.lock.acquire()
        if request_id not in self.states:
            self.states[request_id] = WorkflowState(request_id, self.func)
        state = self.states[request_id]
        self.lock.release()
        return state

    # get function's info from database
    # the result is cached
    def get_function_info(self, function_name: str) -> Any:
        if function_name not in self.function_info:
            print('function_name: ', function_name)
            self.function_info[function_name] = repo.get_function_info(function_name, self.meta_db)
        return self.function_info[function_name]

    # trigger the function when one of its parent is finished
    # function may run or not, depending on if all its parents were finished
    # function could be local or remote
    def trigger_function(self, state: WorkflowState, function_name: str, no_parent_execution = False) -> None:
        func_info = self.get_function_info(function_name)
        if func_info['ip'] == self.host_addr:
            # function runs on local
            self.trigger_function_local(state, function_name, no_parent_execution)
        else:
            # function runs on remote machine
            self.trigger_function_remote(state, function_name, func_info['ip'], no_parent_execution)

    # trigger a function that runs on local
    def trigger_function_local(self, state: WorkflowState, function_name: str, no_parent_execution = False) -> None:
        print('----trying to trigger local function ' + function_name + '----')
        state.lock.acquire()
        if not no_parent_execution:
            state.parent_executed[function_name] += 1
        runnable = self.check_runnable(state, function_name)
        # remember to release state.lock
        if runnable:
            state.executed[function_name] = True
            state.lock.release()
            self.run_function(state, function_name)
        else:
            state.lock.release()

    # trigger a function that runs on remote machine
    def trigger_function_remote(self, state: WorkflowState, function_name: str, remote_addr: str, no_parent_execution = False) -> None:
        print('----trying to trigger remote function ' + function_name + '----')
        remote_url = 'http://{}/request'.format(remote_addr)
        data = {
            'request_id': state.request_id,
            'workflow_name': self.workflow_name,
            'function_name': function_name,
            'no_parent_execution': no_parent_execution,
        }
        requests.post(remote_url, json=data)

    # check if a function's parents are all finished
    def check_runnable(self, state: WorkflowState, function_name: str) -> bool:
        info = self.get_function_info(function_name)
        return state.parent_executed[function_name] == info['parent_cnt'] and not state.executed[function_name]

    # run a function on local
    def run_function(self, state: WorkflowState, function_name: str):

        if function_name == 'END':
            return

        info = self.get_function_info(function_name)
        request_id = state.request_id

        # switch functions
        if function_name.startswith('virtual'):
            for i, next_func in enumerate(info['next']):
                cond = info['conditions'][i]
                if cond_exec(request_id, cond):
                    self.run_function(state, next_func)
                    break
            return # do not need to check next
        
        # foreach functions
        if function_name in self.foreach_func:
            all_keys = repo.get_keys(request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
            foreach_keys = []  # ['split_keys', 'split_keys_2']
            for arg in info['input']:
                if info['input'][arg]['type'] == 'key':
                    foreach_keys.append(info['input'][arg]['parameter'])
            jobs = []
            for i in range(len(all_keys[foreach_keys[0]])):
                keys = {}  # {'split_keys': '1', 'split_keys_2': '2'}
                for k in foreach_keys:
                    keys[k] = all_keys[k][i]
                jobs.append(gevent.spawn(function_manager.run, info['function_name'], request_id,
                                         info['runtime'], info['input'], info['output'],
                                         info['to'], keys))
            gevent.joinall(jobs)
        # merge functions
        elif function_name in self.merge_func:
            all_keys = repo.get_keys(request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
            function_manager.run(info['function_name'], request_id,
                                      info['runtime'], info['input'], info['output'],
                                      info['to'], all_keys)
        # normal functions
        else:
            function_manager.run(info['function_name'], request_id,
                                      info['runtime'], info['input'], info['output'],
                                      info['to'], {})
        
        # trigger next functions
        jobs = [
            gevent.spawn(self.trigger_function, state, func)
            for func in info['next']
        ]
        gevent.joinall(jobs)
