from gevent import monkey
monkey.patch_all()

import time
import sys
import repository
import gevent

sys.path.append('../function_manager')
from function_manager import FunctionManager

class FakeFunc:
    def __init__(self, req_id, func):
        self.req_id = req_id
        self.func = func

    def __getattr__(self, name):
        return repository.get_value(self.req_id, self.func, name)


def cond_exec(req_id, cond):
    if cond.startswith('default'):
        return True

    values = {}
    while True:
        try:
            res = eval(cond)
            break
        except NameError as e:
            name = str(e).split("'")[1]
            values[name] = FakeFunc(req_id, name)

    return res


class WorkflowState:
    def __init__(self, workflow, grouping, host, req_id):
        self.workflow = workflow
        self.grouping = grouping
        self.parent_executed = {}
        for func, node in grouping.items():
            if node == host:
                self.parent_executed[func] = 0
        self.req_id = req_id


class WorkflowManager:
    def __init__(self, request_id, mode):
        self.request_id = request_id
        self.function_info = dict()
        self.executed = set()
        repository.create_result_db()
        self.function_manager = FunctionManager(
            "../function_manager/functions")
        self.mode = mode
        self.parent_executed = dict()

    def get_function_info(self, function_name):
        if function_name not in self.function_info:
            print('function_name: ', function_name)
            self.function_info[function_name] = repository.get_function_info(
                function_name, self.mode)
        return self.function_info[function_name]

    def run_function(self, function_name):
        self.executed.add(function_name)
        # prepare params
        function_info = self.get_function_info(function_name)
        # current node is virtual, with a switch condition
        if function_name.startswith('virtual'):
            jobs = []
            for index in range(len(function_info['next'])):
                condition = function_info['conditions'][index]
                if cond_exec(self.request_id, condition):
                    jobs.append(gevent.spawn(self.run_function,
                                function_info['next'][index]))
                    break
            gevent.joinall(jobs)
            return
        # otherwise...
        self.function_manager.run(function_info['function_name'], self.request_id,
                                  function_info['runtime'], function_info['input'], function_info['output'])
        # check if any function has enough input to be able to fire
        jobs = []
        for name in function_info['next']:
            next_function_info = self.get_function_info(name)
            if name not in self.parent_executed:
                self.parent_executed[name] = 1
            else:
                self.parent_executed[name] = self.parent_executed[name] + 1
            if self.parent_executed[name] == next_function_info['parent_cnt'] and name not in self.executed:
                jobs.append(gevent.spawn(self.run_function, name))
        gevent.joinall(jobs)

    def prepare_basic_input(self):
        basic_input = repository.get_basic_input()
        for parameter in basic_input:
            basic_input[parameter] = '0'
        repository.prepare_basic_file(self.request_id, basic_input)

    def run_workflow(self):
        self.prepare_basic_input()
        start_node_name = repository.get_start_node_name()
        start = time.time()
        job = gevent.spawn(self.run_function, start_node_name)
        gevent.joinall([job])
        end = time.time()
        print('mode: ', self.mode, 'execution time: ', end - start)


workflow = WorkflowManager('123', 'function_info')
workflow.run_workflow()
# db[request_id + "_" + function] = {"parameter1" : "...", "parameter2" : "..."}
