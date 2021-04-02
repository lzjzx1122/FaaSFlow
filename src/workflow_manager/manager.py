import gevent
import json
import repository
import function_proxy


class WorkflowManager:
    def __init__(self, request_id):
        self.request_id = request_id
        self.function_info = dict()

    def get_function_info(self, function_name):
        if function_name not in self.function_info:
            self.function_info[function_name] = repository.get_function_info(function_name)
        return self.function_info[function_name]

    def run_function(self, function_name):
        # prepare params
        function_info = self.get_function_info(function_name)
        param = {'function_name': function_info['function_name'], 'request': self.request_id,
                 'runtime': function_info['runtime'], 'input': function_info['input'],
                 'output': function_info['output']}
        # prepare each file's location
        for input_file_name in param['input']:
            input_file = repository.get_file_by_name(input_file_name, self.request_id)
            param['input'][input_file_name]['value'] = input_file['location']
        # run function
        response = function_proxy.run(json.dumps(param))
        # log each function's output
        file_info_list = list()
        for output_file_name in response:
            file_info_list.append({'file_name': output_file_name, 'type': response[output_file_name]['type'],
                                   'location': response[output_file_name]['value']})
        repository.put_file_info(file_info_list, self.request_id)
        # check if any function has enough input to be able to fire
        for name in function_info['next']:
            next_function_info = self.get_function_info(name)
            file_name_list = next_function_info['input'].keys()
            if repository.has_files(file_name_list, self.request_id):
                gevent.spawn(self.run_function(name))

    def prepare_basic_input(self):
        basic_input = repository.get_basic_input()
        file_info_list = list()
        for doc in basic_input:
            file_info_list.append({'file_name': doc['file_name'], 'type': 'DB',
                                   'location': doc['_id']})
        repository.put_file_info(file_info_list, self.request_id)

    def run_workflow(self):
        repository.create_result_db(self.request_id)
        self.prepare_basic_input()
        gevent.spawn(self.run_function('start_node'))


workflow = WorkflowManager('1')
workflow.run_workflow()
