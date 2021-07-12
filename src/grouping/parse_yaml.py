import yaml
import component

network_bandwidth = 10000000 / 8


def parse(filename):
    data = yaml.load(open(filename), Loader=yaml.FullLoader)
    global_input = dict()
    start_functions = []
    nodes = dict()
    parent_cnt = dict()
    foreach_functions = set()
    merge_funtions = set()
    total = 0
    for key in data['global_input']:
        parameter = data['global_input'][key]['value']['parameter']
        global_input[parameter] = '0'
    functions = data['functions']
    parent_cnt[functions[0]['name']] = 0
    for function in functions:
        name = function['name']
        source = function['source']
        runtime = function['runtime']
        input_files = dict()
        output_files = dict()
        next = list()
        nextDis = list()
        send_byte = 0
        if 'input' in function:
            for key in function['input']:
                input_files[key] = {'function': function['input'][key]['value']['function'],
                                    'parameter': function['input'][key]['value']['parameter'],
                                    'size': function['input'][key]['size'], 'arg': key,
                                    'type': function['input'][key]['type']}
        if 'output' in function:
            for key in function['output']:
                output_files[key] = {'size': function['output'][key]['size'], 'type': function['output'][key]['type']}
                send_byte += function['output'][key]['size']
        send_time = send_byte / network_bandwidth
        conditions = list()
        if 'next' in function:
            foreach_flag = False
            if function['next']['type'] == 'switch':
                conditions = function['next']['conditions']
            elif function['next']['type'] == 'foreach':
                foreach_flag = True
            for n in function['next']['nodes']:
                if name in foreach_functions:
                    merge_funtions.add(n)
                if foreach_flag:
                    foreach_functions.add(n)
                next.append(n)
                nextDis.append(send_time)
                if n not in parent_cnt:
                    parent_cnt[n] = 1
                else:
                    parent_cnt[n] = parent_cnt[n] + 1
        current_function = component.function(name, [], next, nextDis, source, runtime,
                                              input_files, output_files, conditions)
        total = total + 1
        nodes[name] = current_function
    for name in nodes:
        if parent_cnt[name] == 0:
            start_functions.append(name)
        for next_node in nodes[name].next:
            nodes[next_node].prev.append(name)
    return component.workflow(start_functions, nodes, global_input, total, parent_cnt, foreach_functions, merge_funtions)


yaml_file = '../../benchmark/illgal_recognizer/flat_workflow.yaml'
workflow = parse(yaml_file)
