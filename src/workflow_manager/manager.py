from gevent import monkey

monkey.patch_all()
import gevent
import repository
import function_proxy
import sys
import time

sys.path.append('../function_manager')
from function_manager import FunctionManager


class ConditionParser:
    def __init__(self, request_id):
        self.request_id = request_id

    def calculate(self, a, b, op):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        else:
            return a / b

    def get_expr_value(self, expr):
        operator = ['+', '-', '*', '/']
        current_index = 0
        num_stack = list()
        op_stack = list()
        while current_index < len(expr):
            pre_index = current_index
            while current_index < len(expr) and expr[current_index] not in operator:
                current_index = current_index + 1
            key = expr[pre_index, current_index].split('.')
            function = key[0]
            parameter = key[1]
            value = repository.get_value(self.request_id, function, parameter)
            num_stack.append(value)
            if current_index == len(expr):
                while len(op_stack) != 0:
                    a = num_stack.pop()
                    b = num_stack.pop()
                    op = op_stack.pop()
                    num_stack.append(self.calculate(a, b, op))
                break
            elif len(op_stack) == 0:
                num_stack.append(value)
                op_stack.append(expr[current_index])
            else:
                op = expr[current_index]
                if op == '+' or op == '-':
                    a = num_stack.pop()
                    b = num_stack.pop()
                    op2 = op_stack.pop()
                    num_stack.append(self.calculate(a, b, op2))
                    op_stack.append(op)
                else:
                    if op_stack[-1] == '*' or op_stack[-1] == '/':
                        a = num_stack.pop()
                        b = num_stack.pop()
                        op2 = op_stack.pop()
                        num_stack.append(self.calculate(a, b, op2))
                        op_stack.append(op)
                    else:
                        op_stack.append(op)
        return 0

    def parse_condition(self, condition):
        if condition.startswith('default'):
            return True
        condition = condition.replace(' ', '')
        if '<' in condition:
            place = condition.find('<')
            left_value = self.get_expr_value(condition[:place])
            right_value = self.get_expr_value(condition[place + 1:])
            return left_value < right_value
        elif '>' in condition:
            place = condition.find('>')
            left_value = self.get_expr_value(condition[:place])
            right_value = self.get_expr_value(condition[place + 1:])
            return left_value > right_value
        elif '==' in condition:
            place = condition.find('==')
            left_value = self.get_expr_value(condition[:place])
            right_value = self.get_expr_value(condition[place + 2:])
            return left_value == right_value
        else:
            return False


class WorkflowManager:
    def __init__(self, request_id, mode):
        self.request_id = request_id
        self.function_info = dict()
        self.executed = set()
        repository.create_result_db()
        self.function_manager = FunctionManager("../function_manager/functions")
        self.mode = mode
        self.parent_executed = dict()
        self.condition_parser = ConditionParser(request_id)

    def get_function_info(self, function_name):
        if function_name not in self.function_info:
            print('function_name: ', function_name)
            self.function_info[function_name] = repository.get_function_info(function_name, self.mode)
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
                if self.condition_parser.parse_condition(condition):
                    jobs.append(gevent.spawn(self.run_function, function_info['next'][index]))
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
