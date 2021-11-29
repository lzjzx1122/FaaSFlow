import sys
import logging
import time
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

min_port = 20000

# mode: 'optimized' vs 'normal'
class MasterSPManager:
    def __init__(self, host_addr: str, workflow_name: str, data_mode: str, function_info_addr: str):
        global min_port

        self.lock = gevent.lock.BoundedSemaphore() # guard self.states
        self.host_addr = host_addr
        self.workflow_name = workflow_name
        self.states: Dict[str, WorkflowState] = {}
        self.function_info: Dict[str, dict] = {}

        self.data_mode = data_mode
        if data_mode == 'optimized':
            self.info_db = workflow_name + '_function_info'
        else:
            self.info_db = workflow_name + '_function_info_raw'
        self.meta_db = workflow_name + '_workflow_metadata'

        self.foreach_func = repo.get_foreach_functions(self.meta_db)
        self.merge_func = repo.get_merge_functions(self.meta_db)
        self.func = repo.get_current_node_functions(self.host_addr, self.info_db)
        
        self.function_manager = FunctionManager(function_info_addr, min_port)
        min_port += 5000

    # return the workflow state of the request
    def get_state(self, request_id: str) -> WorkflowState:
        self.lock.acquire()
        if request_id not in self.states:
            self.states[request_id] = WorkflowState(request_id, self.func)
        state = self.states[request_id]
        self.lock.release()
        return state
    
    def del_state_remote(self, request_id: str, remote_addr: str):
        url = 'http://{}/clear'.format(remote_addr)
        requests.post(url, json={'request_id': request_id, 'workflow_name': self.workflow_name})

    # delete state
    def del_state(self, request_id: str, master: bool):
        logging.info('delete state of: %s', request_id)
        self.lock.acquire()
        if request_id in self.states:
            del self.states[request_id]
        self.lock.release()
        if master:
            jobs = []
            addrs = repo.get_all_addrs(self.meta_db)
            for addr in addrs:
                if addr != self.host_addr:
                    jobs.append(gevent.spawn(self.del_state_remote, request_id, addr))
            gevent.joinall(jobs)

    # get function's info from database
    # the result is cached
    def get_function_info(self, function_name: str) -> Any:
        if function_name not in self.function_info:
            self.function_info[function_name] = repo.get_function_info(function_name, self.info_db)
        return self.function_info[function_name]

    # get node status
    def get_node_status(self, addr: str, status: Dict):
        url = f'http://{addr}/info'
        result = requests.get(url)
        status[addr] = result.json()

    # simulate dynamic node selecting
    def node_select(self):
        addrs = repo.get_all_addrs(self.meta_db)
        jobs = []
        status = {}
        for addr in addrs:
            jobs.append(gevent.spawn(self.get_node_status, addr, status))
        gevent.joinall(jobs)
        selected_addr = ''
        return selected_addr

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
        logging.info('trigger local function: %s of: %s time: %s', function_name, state.request_id, time.time())
        self.run_function(state, function_name)

    # trigger a function that runs on remote machine
    def trigger_function_remote(self, state: WorkflowState, function_name: str, remote_addr: str, no_parent_execution = False) -> None:
        logging.info('trigger remote function: %s on: %s of: %s time: %s', function_name, remote_addr, state.request_id, time.time())
        state.lock.acquire()
        if not no_parent_execution:
            state.parent_executed[function_name] += 1
        runnable = self.check_runnable(state, function_name)
        if runnable:
            state.executed[function_name] = True
            state.lock.release()
            self.node_select() # simulate node selecting 
            info = self.get_function_info(function_name)
            if function_name.startswith('virtual'): # virtual must run on master
                self.run_switch(state, info)
                return # do not need to check next
            else:
                remote_url = 'http://{}/request'.format(remote_addr)
                data = {
                    'request_id': state.request_id,
                    'workflow_name': self.workflow_name,
                    'function_name': function_name,
                    'no_parent_execution': no_parent_execution,
                }
                requests.post(remote_url, json=data)
                jobs = [
                    gevent.spawn(self.trigger_function, state, func)
                    for func in info['next']
                ]
                gevent.joinall(jobs)
        else:
            state.lock.release()

    # check if a function's parents are all finished
    def check_runnable(self, state: WorkflowState, function_name: str) -> bool:
        info = self.get_function_info(function_name)
        return state.parent_executed[function_name] == info['parent_cnt'] and not state.executed[function_name]

    # run a function on local
    def run_function(self, state: WorkflowState, function_name: str) -> None:
        logging.info('run function: %s of: %s', function_name, state.request_id)
        # end functions
        if function_name == 'END':
            return

        info = self.get_function_info(function_name)
        # switch functions
        if function_name.startswith('virtual'):
            self.run_switch(state, info)
            return # do not need to check next
        
        if function_name in self.foreach_func:
            self.run_foreach(state, info)
        elif function_name in self.merge_func:
            self.run_merge(state, info)
        else: # normal functions
            self.run_normal(state, info)

    def run_switch(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        for i, next_func in enumerate(info['next']):
                cond = info['conditions'][i]
                if cond_exec(state.request_id, cond):
                    end = time.time()
                    repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})
                    self.trigger_function(state, next_func)
                    break

    def run_foreach(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        all_keys = repo.get_keys(state.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
        foreach_keys = []  # ['split_keys', 'split_keys_2']
        for arg in info['input']:
            if info['input'][arg]['type'] == 'key':
                foreach_keys.append(info['input'][arg]['parameter'])
        jobs = []
        for i in range(len(all_keys[foreach_keys[0]])):
            keys = {}  # {'split_keys': '1', 'split_keys_2': '2'}
            for k in foreach_keys:
                keys[k] = all_keys[k][i]
            jobs.append(gevent.spawn(self.function_manager.run, info['function_name'], state.request_id,
                                     info['runtime'], info['input'], info['output'],
                                     info['to'], keys))
        gevent.joinall(jobs)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    def run_merge(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        all_keys = repo.get_keys(state.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
        self.function_manager.run(info['function_name'], state.request_id,
                             info['runtime'], info['input'], info['output'],
                             info['to'], all_keys)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    def run_normal(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        self.function_manager.run(info['function_name'], state.request_id,
                             info['runtime'], info['input'], info['output'],
                             info['to'], {})
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    def clear_mem(self, request_id):
        repo.clear_mem(request_id)
    
    def clear_db(self, request_id):
        repo.clear_db(request_id)