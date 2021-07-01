from gevent import monkey
monkey.patch_all()

import time
import sys
import repository
import gevent

sys.path.append('../function_manager')
from function_manager import FunctionManager

repo = repository.Repository(clear=False)
class FakeFunc:
    def __init__(self, req_id, func):
        self.req_id = req_id
        self.func = func

    def __getattr__(self, name):
        return repo.fetch(self.req_id, name)


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

function_manager = FunctionManager("../../examples/switch/functions") # demonstrate workflow definition(computation graph, code...)

# mode: 'optimized' vs 'normal'
class WorkflowManager:
    def __init__(self, request_id, mode):
        self.request_id = request_id
        self.function_info = dict()
        self.executed = set()
        self.parent_executed = dict()
        self.foreach_functions = []
        self.after_foreach = False
        self.mode = mode
        if mode == 'optimized':
            self.meta_db = 'function_info'
        else:
            self.meta_db = 'function_info_raw'

    def get_function_info(self, function_name):
        if function_name not in self.function_info:
            print('function_name: ', function_name)
            self.function_info[function_name] = repo.get_function_info(function_name, self.meta_db)
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
        # current node is under foreach
        if function_name in self.foreach_functions:
            all_keys = repo.get_keys(self.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
            foreach_keys = []  # ['split_keys', 'split_keys_2']
            for arg in function_info['input']:
                if function_info['input'][arg]['type'] == 'key':
                    foreach_keys.append(function_info['input'][arg]['parameter'])
            jobs = []
            for i in range(len(all_keys[foreach_keys[0]])):
                keys = {}  # {'split_keys': '1', 'split_keys_2': '2'}
                for k in foreach_keys:
                    keys[k] = all_keys[k][i]
                jobs.append(gevent.spawn(function_manager.run, function_info['function_name'], self.request_id,
                                         function_info['runtime'], function_info['input'], function_info['output'],
                                         function_info['to'], keys))
            gevent.joinall(jobs)
            self.after_foreach = True
        # otherwise...
        else:
            all_keys = {}
            if self.after_foreach:
                all_keys = repo.get_keys(self.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
                self.after_foreach = False
            function_manager.run(function_info['function_name'], self.request_id,
                                      function_info['runtime'], function_info['input'], function_info['output'],
                                      function_info['to'], all_keys)
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

    # def prepare_basic_input(self):
        # basic_input = repo.get_basic_input()
        # for parameter in basic_input:
        #     basic_input[parameter] = '0'
        # repo.prepare_basic_file(self.request_id, basic_input)
        # repo.create_request_doc(self.request_id)

    def run_workflow(self):
        # self.prepare_basic_input()
        start_node_name = repo.get_start_node_name()
        self.foreach_functions = repo.get_foreach_functions()
        start = time.time()
        job = gevent.spawn(self.run_function, start_node_name)
        gevent.joinall([job])
        repo.clear_mem(self.request_id)
        end = time.time()
        print('mode: ', self.mode, 'execution time: ', end - start)

## examples of how to run workflow_manager
manager = WorkflowManager('123', 'optimized')
manager.run_workflow()
