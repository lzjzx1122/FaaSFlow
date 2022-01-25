import sys
sys.path.append('../../../config')
import parse_yaml
import queue
import component
import config
import yaml
import repository

mem_usage = 0
max_mem_usage = 0
group_ip = {}
group_scale = {}

def init_graph(workflow, group_set, node_info):
    global group_ip, group_scale
    ip_list = list(node_info.keys())
    in_degree_vec = dict()
    q = queue.Queue()
    for name in workflow.start_functions:
        q.put(workflow.nodes[name])
        group_set.append((name, ))
    while q.empty() is False:
        node = q.get()
        for next_node_name in node.next:
            if next_node_name not in in_degree_vec:
                in_degree_vec[next_node_name] = 1
                q.put(workflow.nodes[next_node_name])
                group_set.append((next_node_name, ))
            else:
                in_degree_vec[next_node_name] += 1
    for s in group_set:
        group_ip[s] = ip_list[hash(s) % len(ip_list)]
        group_scale[s] = workflow.nodes[s[0]].scale
        node_info[group_ip[s]] -= workflow.nodes[s[0]].scale
    return in_degree_vec


def find_set(node, group_set):
    for node_set in group_set:
        if node in node_set:
            return node_set
    return None


def topo_search(workflow: component.workflow, in_degree_vec, group_set):
    dist_vec = dict()  # { name: [dist, max_length] }
    prev_vec = dict()  # { name: [prev_name, length] }
    q = queue.Queue()
    for name in workflow.start_functions:
        q.put(workflow.nodes[name])
        dist_vec[name] = [workflow.nodes[name].runtime, 0]
        prev_vec[name] = []
    while q.empty() is False:
        node = q.get()
        pre_dist = dist_vec[node.name]
        prev_name = node.name
        for index in range(len(node.next)):
            next_node = workflow.nodes[node.next[index]]
            w = node.nextDis[index]
            next_node_name = next_node.name
            if next_node_name in find_set(prev_name, group_set):
                w = w / config.NET_MEM_BANDWIDTH_RATIO
            if next_node.name not in dist_vec:
                dist_vec[next_node_name] = [pre_dist[0] + w + next_node.runtime, max(pre_dist[1], w)]
                prev_vec[next_node_name] = [prev_name, w]
            elif dist_vec[next_node_name][0] < pre_dist[0] + w + next_node.runtime:
                dist_vec[next_node_name] = [pre_dist[0] + w + next_node.runtime, max(pre_dist[1], w)]
                prev_vec[next_node_name] = [prev_name, w]
            elif dist_vec[next_node_name][0] == pre_dist[0] + w + next_node.runtime and max(pre_dist[1], w) > \
                    dist_vec[next_node_name][1]:
                dist_vec[next_node_name][1] = max(pre_dist[1], w)
                prev_vec[next_node_name] = [prev_name, w]
            in_degree_vec[next_node_name] -= 1
            if in_degree_vec[next_node_name] == 0:
                q.put(next_node)
    return dist_vec, prev_vec

def mergeable(node1, node2, group_set, workflow: component.workflow, write_to_mem_nodes, node_info):
    global mem_usage, max_mem_usage, group_ip, group_scale
    node_set1 = find_set(node1, group_set)

    # same set?
    if node2 in node_set1: # same set
        return False
    node_set2 = find_set(node2, group_set)

    # meet scale requirement?
    new_node_info = node_info.copy()
    node_set1_scale = group_scale[node_set1]
    node_set2_scale = group_scale[node_set2]
    new_node_info[group_ip[node_set1]] += node_set1_scale
    new_node_info[group_ip[node_set2]] += node_set2_scale
    best_fit_addr, best_fit_scale = None, 10000000
    for addr in new_node_info:
        if new_node_info[addr] >= node_set1_scale + node_set2_scale and new_node_info[addr] < best_fit_scale:
            best_fit_addr = addr
            best_fit_scale = new_node_info[addr]
    if best_fit_addr is None:
        # print('Hit scale threshold', node_set1_scale, node_set2_scale)
        return False

    # check memory limit    
    if node1 not in write_to_mem_nodes:
        current_mem_usage = workflow.nodes[node1].nextDis[0] * config.NETWORK_BANDWIDTH
        if mem_usage + current_mem_usage > max_mem_usage: # too much memory consumption
            # print('Hit memory consumption threshold')
            return False
        mem_usage += current_mem_usage
        write_to_mem_nodes.append(node1)

    # merge sets & update scale
    new_group_set = (*node_set1, *node_set2)

    group_set.append(new_group_set)
    group_ip[new_group_set] = best_fit_addr
    node_info[best_fit_addr] -= node_set1_scale + node_set2_scale
    group_scale[new_group_set] = node_set1_scale + node_set2_scale

    node_info[group_ip[node_set1]] += node_set1_scale
    node_info[group_ip[node_set2]] += node_set2_scale
    group_set.remove(node_set1)
    group_set.remove(node_set2) 
    group_ip.pop(node_set1)
    group_ip.pop(node_set2)
    group_scale.pop(node_set1)
    group_scale.pop(node_set2)
    return True

def merge_path(crit_vec, group_set, workflow: component.workflow, write_to_mem_nodes, node_info):
    for edge in crit_vec:
        if mergeable(edge[1][0], edge[0], group_set, workflow, write_to_mem_nodes, node_info):
            return True
    return False


def get_longest_dis(workflow, dist_vec):
    dist = 0
    node_name = ''
    for name in workflow.nodes:
        if dist_vec[name][0] > dist:
            dist = dist_vec[name][0]
            node_name = name
    return dist, node_name


def grouping(workflow: component.workflow, node_info):

    # initialization: get in-degree of each node
    group_set = list()
    critical_path_functions = set()
    write_to_mem_nodes = []
    in_degree_vec = init_graph(workflow, group_set, node_info)

    while True:

        # break if every node is in same group
        if len(group_set) == 1:
            break

        # topo dp: find each node's longest dis and it's predecessor
        dist_vec, prev_vec = topo_search(workflow, in_degree_vec.copy(), group_set)
        crit_length, tmp_node_name = get_longest_dis(workflow, dist_vec)
        # print('crit_length: ', crit_length)

        # find the longest path, edge descent sorted
        critical_path_functions.clear()
        crit_vec = dict()
        while tmp_node_name not in workflow.start_functions:
            crit_vec[tmp_node_name] = prev_vec[tmp_node_name]
            tmp_node_name = prev_vec[tmp_node_name][0]
        crit_vec = sorted(crit_vec.items(), key=lambda c: c[1][1], reverse=True)
        for k, v in crit_vec:
            critical_path_functions.add(k)
            critical_path_functions.add(v[0])

        # if can't merge every edge of this path, just break
        if not merge_path(crit_vec, group_set, workflow, write_to_mem_nodes, node_info):
            break
    return group_set, critical_path_functions

# define the output destination at function level, instead of one per key/file
def get_type(workflow, node, group_detail):
    not_in_same_set = False
    in_same_set = False
    for next_node_name in node.next:
        next_node = workflow.nodes[next_node_name]
        node_set = find_set(next_node.name, group_detail)
        if node.name not in node_set:
            not_in_same_set = True
        else:
            in_same_set = True
    if not_in_same_set and in_same_set:
        return 'DB+MEM'
    elif in_same_set:
        return 'MEM'
    else:
        return 'DB'

def get_max_mem_usage(workflow: component.workflow):
    global max_mem_usage
    for name in workflow.nodes:
        if not name.startswith('virtual'):
            max_mem_usage += (1 - config.RESERVED_MEM_PERCENTAGE - workflow.nodes[name].mem_usage) * config.CONTAINER_MEM * workflow.nodes[name].split_ratio
    return max_mem_usage

# def query(workflow: component.workflow, group_detail: List):
#     total = 0
#     merged = 0
#     for name, node in workflow.nodes.items():
#         for next_node_name in node.next:
#             total = total + 1
#             merged_edge = False
#             for s in group_detail:
#                 if name in s and next_node_name in s:
#                     merged_edge = True
#             if merged_edge:
#                 merged = merged + 1
#     return merged, total

def get_grouping_config(workflow: component.workflow):

    global max_mem_usage, group_ip

    # get node info
    node_info_list = yaml.load(open('node_info.yaml'), Loader=yaml.FullLoader)
    node_info_dict = {}
    for node_info in node_info_list['nodes']:
        node_info_dict[node_info['worker_address']] = node_info['scale_limit']

    # grouping algorithm
    max_mem_usage = get_max_mem_usage(workflow)
    # print('max_mem_usage', max_mem_usage)
    group_detail, critical_path_functions = grouping(workflow, node_info_dict)
    # print(group_detail)
    
    # print(query(workflow, group_detail))

    # building function info: both optmized and raw version
    ip_list = list(node_info_dict.keys())
    function_info_dict = {}
    function_info_raw_dict = {}
    for node_name in workflow.nodes:
        node = workflow.nodes[node_name]
        to = get_type(workflow, node, group_detail)
        ip = group_ip[find_set(node_name, group_detail)]
        function_info = {'function_name': node.name, 'runtime': node.runtime, 'to': to, 'ip': ip,
                         'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
        function_info_raw = {'function_name': node.name, 'runtime': node.runtime, 'to': 'DB', 'ip': ip_list[hash(node.name) % len(ip_list)],
                             'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
        function_input = dict()
        function_input_raw = dict()
        for arg in node.input_files:
            function_input[arg] = {'size': node.input_files[arg]['size'],
                                   'function': node.input_files[arg]['function'],
                                   'parameter': node.input_files[arg]['parameter'],
                                   'type': node.input_files[arg]['type']}
            function_input_raw[arg] = {'size': node.input_files[arg]['size'],
                                       'function': node.input_files[arg]['function'],
                                       'parameter': node.input_files[arg]['parameter'],
                                       'type': node.input_files[arg]['type']}
        function_output = dict()
        function_output_raw = dict()
        for arg in node.output_files:
            function_output[arg] = {'size': node.output_files[arg]['size'], 'type': node.output_files[arg]['type']}
            function_output_raw[arg] = {'size': node.output_files[arg]['size'], 'type': node.output_files[arg]['type']}
        function_info['input'] = function_input
        function_info['output'] = function_output
        function_info['next'] = node.next
        function_info_raw['input'] = function_input_raw
        function_info_raw['output'] = function_output_raw
        function_info_raw['next'] = node.next
        function_info_dict[node_name] = function_info
        function_info_raw_dict[node_name] = function_info_raw
    
    # if successor contains 'virtual', then the destination of storage should be propagated
    for name in workflow.nodes:
        for next_name in workflow.nodes[name].next:
            if next_name.startswith('virtual'):
                if function_info_dict[next_name]['to'] != function_info_dict[name]['to']:
                    function_info_dict[name]['to'] = 'DB+MEM'

    return node_info_dict, function_info_dict, function_info_raw_dict, critical_path_functions

def main(node_cnt):
    workflow = parse_yaml.parse('genome', node_cnt)
    repo = repository.Repository('genome')
    node_info, function_info, function_info_raw, critical_path_functions = get_grouping_config(workflow)

if __name__ == '__main__':
    node_cnt = int(sys.argv[1])
    main(node_cnt)