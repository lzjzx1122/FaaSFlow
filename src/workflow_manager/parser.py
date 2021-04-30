import yaml
import component

network_bandwidth = 10000000 / 8


def parse(filename):
    data = yaml.load(open(filename), Loader=yaml.FullLoader)
    global_input = dict()
    total = 0
    start = None
    nodes = dict()
    parent_cnt = dict()
    for key in data['global_input']:
        parameter = data['global_input'][key]['value']['parameter']
        global_input[parameter] = '0'
    functions = data['functions']
    for function in functions:
        name = function['name']
        source = function['source']
        runtime = function['runtime']
        input_files = list()
        output_files = list()
        next = list()
        nextDis = list()
        send_byte = 0
        if 'input' in function:
            for key in function['input']:
                input_files.append({'function': function['input'][key]['value']['function'],
                                    'parameter': function['input'][key]['value']['parameter'],
                                    'size': function['input'][key]['size']})
        if 'output' in function:
            for key in function['output']:
                output_files.append({'function': function['input'][key]['value']['function'],
                                     'parameter': function['input'][key]['value']['parameter'],
                                     'size': function['output'][key]['size']})
                send_byte += function['output'][key]['size']
        send_time = send_byte / network_bandwidth
        conditions = list()
        if 'next' in function:
            if function['next']['type'] == 'switch':
                conditions = function['next']['conditions']
            for name in function['next']['nodes']:
                next.append(name)
                nextDis.append(send_time)
                if name not in parent_cnt:
                    parent_cnt[name] = 1
                else:
                    parent_cnt[name] = parent_cnt[name] + 1
        current_function = component.function(name, next, nextDis, source, runtime,
                                              input_files, output_files, conditions)
        if total == 0:
            start = current_function
        total = total+1
        nodes[name] = current_function
    return component.workflow(start, nodes, global_input, total, parent_cnt)


yaml_file = '../../examples/foreach/flat_workflow.yaml'
workflow = parse(yaml_file)
