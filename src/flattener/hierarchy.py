def deep_copy(d):
    assert type(d) == dict
    d_ = dict()
    for (k, v) in d.items():
        assert type(v) == dict
        v2 = v['value']
        if type(v2) == dict:
            v2_ = v2.copy()
        elif type(v2) == list:
            v2_ = []
            for v3 in v2:
                assert type(v3) == dict
                v2_.append(v3.copy())
        else:
            raise Exception("deep_copy error!")
        d_[k] = {'type': v['type'], 'value': v2_}
    return d_

virtual_nodes = 0
def get_virtual_node():
    global virtual_nodes
    virtual_nodes += 1
    return Function('virtual' + str(virtual_nodes), None, None, None, None, True)
 
global_input = dict()

all_functions = []

class Base(object):
    def __init__(self, name, type, inputMappings, outputMappings):
        self.name = name
        self.type = type
        self.inputMappings = inputMappings
        self.outputMappings = outputMappings
        self.start = self
        self.end = self
        self.next = {'type': None, 'nodes': []}
        self.prev = []
        self.input = None
    
    def link(self, node):
        # print('#### link', self.name, node.name, self.end.name, node.start.name)
        self.end.next['nodes'].append(node.start)
        node.start.prev.append(self.end)

    def get_output(self, local):
        pass

    def set_start_and_end(self):
        pass

    def flatten(self):
        pass

    def get_yaml(self):
        pass
    
class Pass(Base):
    def __init__(self, name, inputMappings, outputMappings, steps):
        Base.__init__(self, name, 'pass', inputMappings, outputMappings)
        self.steps = steps

    def get_output(self, input):
        if self.inputMappings == None:
            local = input
        else:
            local = dict()
            for inputMapping in self.inputMappings:
                target = inputMapping['target']
                source = inputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'INPUT')
                if source_split[0] == 'LOCAL':
                    local[target] = input[source_split[1]]
                else:
                    local[target] = global_input[source_split[1]]
                    
        # print('Pass input:', self.name, local)
        self.input = deep_copy(local)

        for step in self.steps:
            sub_output = step.get_output(deep_copy(local))
            for (k, v) in sub_output.items():
                local[k] = v
        
        if self.outputMappings == None:
            # print('Pass output:', self.name, local)
            return local
        else:
            output = dict()
            for outputMapping in self.outputMappings:
                target = outputMapping['target']
                source = outputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and source_split[0] == 'LOCAL'
                output[target] = local[source_split[1]]
            # print('Pass output:', self.name, output)
            return output

    def set_start_and_end(self):
        self.start = self.steps[0]
        self.end = self.steps[len(self.steps) - 1]
        for step in self.steps:
            step.set_start_and_end()
            
    def flatten(self):
        for i in range(len(self.steps) - 1):
            self.steps[i].link(self.steps[i + 1])
        for step in self.steps:
            step.next['type'] = 'pass'
            step.flatten()
    
    def get_yaml(self):
        functions = []
        for step in self.steps:
            functions.extend(step.get_yaml())
        return functions

class Parallel(Base):
    def __init__(self, name, inputMappings, outputMappings, branches):
        Base.__init__(self, name, 'parallel', inputMappings, outputMappings)
        self.branches = branches
    
    def get_output(self, input):
        if self.inputMappings == None:
            local = input
        else:
            local = dict()
            for inputMapping in self.inputMappings:
                target = inputMapping['target']
                source = inputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'INPUT')
                if source_split[0] == 'LOCAL':
                    local[target] = input[source_split[1]]
                else:
                    local[target] = global_input[source_split[1]]

        # print('Parallel input:', self.name, local)
        self.input = deep_copy(local)
        
        sub_outputs = []
        for branch in self.branches:
            sub_outputs.append(branch.get_output(deep_copy(local)))

        if self.outputMappings == None:
            for sub_output in sub_outputs:
                for (k, v) in sub_output.items():
                    local[k] = v
            # print('Parallel output:', self.name, local) 
            return local
        else:
            output = dict()
            for outputMapping in self.outputMappings:
                target = outputMapping['target']
                source = outputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'LOCAL[*]')
                if source_split[0] == 'LOCAL[*]':
                    output[target] = {'type': 'parallel', 'value': []}
                    for sub_output in sub_outputs:
                        if source_split[1] in sub_output:
                            output[target]['value'].append(sub_output[source_split[1]]['value'])
                else:
                    output[target] = local[source_split[1]] if source_split[1] in local else None
                    for sub_output in sub_outputs:
                        if source_split[1] in sub_output:
                            output[target] = {'type': 'parallel', 'value': sub_output[source_split[1]]['value']}
            # print('Parallel output:', self.name, output)
            return output

    def set_start_and_end(self):
        self.start = get_virtual_node()
        self.end = get_virtual_node()
        for branch in self.branches:
            branch.set_start_and_end()

    def flatten(self):
        self.start.next['type'] = 'parallel'
        self.end.next['type'] = 'pass'
        self.start.flatten()
        self.end.flatten()
        for branch in self.branches:
            self.start.link(branch)
            branch.link(self.end)
            branch.flatten()
            branch.next['type'] = 'pass'

    def get_yaml(self):
        functions = []
        functions.extend(self.start.get_yaml())
        for branch in self.branches:
            functions.extend(branch.get_yaml())
        functions.extend(self.end.get_yaml())
        return functions

class Switch(Base):
    def __init__(self, name, inputMappings, outputMappings, choices):
        Base.__init__(self, name, 'switch', inputMappings, outputMappings)
        self.choices = choices

    def get_output(self, input):
        if self.inputMappings == None:
            local = input
        else:
            local = dict()
            for inputMapping in self.inputMappings:
                target = inputMapping['target']
                source = inputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'INPUT')
                if source_split[0] == 'LOCAL':
                    local[target] = input[source_split[1]]
                else:
                    local[target] = global_input[source_split[1]]

        # print('Switch input:', self.name, local)
        self.input = deep_copy(local)
        
        sub_outputs = []
        for choice in self.choices:
            sub_outputs.append(choice['go'].get_output(deep_copy(local)))

        if self.outputMappings == None:
            for sub_output in sub_outputs:
                for (k, v) in sub_output.items():
                    local[k] = v
            # print('Switch output:', self.name, local)
            return local
        else:
            output = dict()
            for outputMapping in self.outputMappings:
                target = outputMapping['target']
                source = outputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and source_split[0] == 'LOCAL'
                output[target] = {'type': 'switch', 'value': []}
                for sub_output in sub_outputs:
                    if source_split[1] in sub_output:
                        output[target]['value'].append(sub_output[source_split[1]]['value'])
            # print('Switch output:', self.name, output)
            return output
    
    def set_start_and_end(self):
        self.start = get_virtual_node()
        self.end = get_virtual_node()
        for choice in self.choices:
            choice['go'].set_start_and_end()
    
    def flatten(self):
        self.start.next['type'] = 'switch'
        self.end.next['type'] = 'pass'
        self.start.flatten()
        self.end.flatten()
        for choice in self.choices:
            self.start.link(choice['go'])
            choice['go'].link(self.end)
            choice['go'].flatten()
            choice['go'].next['type'] = 'pass'

    def get_yaml(self):
        functions = []
        functions.extend(self.start.get_yaml())
        for choice in self.choices:
            functions.extend(choice['go'].get_yaml())
        functions.extend(self.end.get_yaml())
        return functions

class Foreach(Base):
    def __init__(self, name, inputMappings, outputMappings, task):
        Base.__init__(self, name, 'function', inputMappings, outputMappings)
        self.task = task

    def get_output(self, input):
        if self.inputMappings == None:
            local = input
        else:
            local = dict()
            for inputMapping in self.inputMappings:
                target = inputMapping['target']
                source = inputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'INPUT')
                if source_split[0] == 'LOCAL':
                    if '[*]' in source_split[1]:
                        local[target] = input[source_split[1][0: len(source_split[1]) - 3]]
                    else:
                        local[target] = input[source_split[1]]    
                else:
                    local[target] = global_input[source_split[1]]
                    
        # print('Foreach input:', self.name, local)
        self.input = deep_copy(local)
        
        sub_output = self.task.get_output(deep_copy(local))
        for (k, v) in sub_output.items():
            local[k] = v
        
        if self.outputMappings == None:
            # print('Foreach output:', self.name, local)
            return local
        else:
            output = dict()
            for outputMapping in self.outputMappings:
                target = outputMapping['target']
                source = outputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'LOCAL[*]')
                if source_split[0] == 'LOCAL':
                    output[target] = {'type': 'pass', 'value': local[source_split[1]]}
                else:
                    output[target] = {'type': 'foreach', 'value': sub_output[source_split[1]]['value']}
            # print('Pass output:', self.name, output)
            return output

    def set_start_and_end(self):
        self.start = get_virtual_node()
        self.end = get_virtual_node()
        self.task.set_start_and_end()

    def flatten(self):
        self.start.next['type'] = 'foreach'
        self.end.next['type'] = 'pass'
        self.task.next['type'] = 'pass'
        self.start.link(self.task)
        self.task.link(self.end)
        self.start.flatten()
        self.end.flatten()
        self.task.flatten()

    def get_yaml(self):
        functions = []
        functions.extend(self.start.get_yaml())
        functions.extend(self.task.get_yaml())
        functions.extend(self.end.get_yaml())
        return functions

class Function(Base):
    def __init__(self, name, inputMappings, outputMappings, source, output, is_virtual):
        Base.__init__(self, name, 'function', inputMappings, outputMappings)
        self.source = source
        self.output = output
        self.is_virtual = is_virtual
        self.is_removed = False

    def get_output(self, input):
        if self.inputMappings == None:
            local = input
        else:
            local = dict()
            for inputMapping in self.inputMappings:
                target = inputMapping['target']
                source = inputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and (source_split[0] == 'LOCAL' or source_split[0] == 'INPUT')
                if source_split[0] == 'LOCAL':
                    local[target] = input[source_split[1]]
                else:
                    local[target] = global_input[source_split[1]]
        
        print('Function input:', self.name, local)
        self.input = deep_copy(local)
        
        if self.output != None:
            for parameter in self.output:
                local[parameter] = {'type': 'pass', 'value': {'function': self.name, 'parameter': parameter}}
        
        if self.outputMappings == None:
            # print('Function output:', self.name, local)
            return local
        else:
            output = dict()
            for outputMapping in self.outputMappings:
                target = outputMapping['target']
                source = outputMapping['source']
                source_split = source.split('.')
                assert len(source_split) == 2 and source_split[0] == 'LOCAL'
                output[target] = local[source_split[1]]
            # print('Function output:', self.name, output)
            return output

    def set_start_and_end(self):
        self.start = self
        self.end = self
    
    def flatten(self):
        all_functions.append(self)
        pass

    def get_yaml(self):
        if self.is_removed == True:
            return []
        function = {'name': self.name}
        if self.is_virtual:
            function['source'] = 'VIRTUAL'
        else:
            function['source'] = self.source
        if self.input != None and len(self.input) > 0:
            function['input'] = self.input
        if len(self.next['nodes']) > 0:
            function['next'] = {'type': self.next['type'], 'nodes': []}
            for n in self.next['nodes']:
                function['next']['nodes'].append(n.name)
        return [function]