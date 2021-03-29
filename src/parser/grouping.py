import parser_with_time
import queue
import uuid
import json

inter_communication_time = 0.1
node_cnt = 10
node_ip = ['', '', '', '', '', '', '', '', '', '']


def init_graph(workflow, group_set):
    in_degree_vec = dict()
    q = queue.Queue()
    q.put(workflow.start)
    group_set.append({workflow.start.name})
    while q.empty() is False:
        node = q.get()
        for next_node in node.next:
            if next_node.name not in in_degree_vec:
                in_degree_vec[next_node.name] = 1
                q.put(next_node)
                group_set.append({next_node.name})
            else:
                in_degree_vec[next_node.name] += 1
    return in_degree_vec


def find_set(node, group_set):
    for node_set in group_set:
        if node in node_set:
            return node_set
    return None


def topo_search(workflow, in_degree_vec, group_set, no_net_latency):
    dist_vec = dict()  # { name: [dist, max_length] }
    prev_vec = dict()  # { name: [prev_name, length] }
    q = queue.Queue()
    q.put(workflow.start)
    dist_vec[workflow.start.name] = [workflow.start.runtime, 0]
    prev_vec[workflow.start.name] = []
    while q.empty() is False:
        node = q.get()
        pre_dist = dist_vec[node.name]
        prev_name = node.name
        for index in range(len(node.next)):
            next_node = node.next[index]
            w = node.nextDis[index]
            next_node_name = next_node.name
            if no_net_latency is True:
                w = 0
            elif next_node_name in find_set(prev_name, group_set):
                w = inter_communication_time
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


def mergeable(node1, node2, group_set, group_size):
    node_set1 = find_set(node1, group_set)
    if node2 in node_set1:
        return False
    node_set2 = find_set(node2, group_set)
    if len(node_set1) + len(node_set2) > group_size:
        return False
    group_set.remove(node_set1)
    group_set.remove(node_set2)
    group_set.append(node_set1 | node_set2)
    return True


penalty_rate = 1.5


def merge_node(crit_vec, group_set, group_size):
    merge_flag = False
    for edge in crit_vec:
        merge_flag = merge_flag | mergeable(edge[0], edge[1][0], group_set, group_size)
        if merge_flag:
            break
    return merge_flag


def get_prerequisite(workflow):
    result = []
    for node in workflow.nodes:
        prerequisite = []
        for pre_node in node.prev:
            prerequisite.append(pre_node.name)
        result.append({'name': node.name, 'prerequisite': prerequisite})
    return result


def grouping(req_id, workflow):
    topo_search_cnt = 0
    group_set = list()
    in_degree_vec = init_graph(workflow, group_set)
    group_size = 2
    total_node_cnt = len(workflow.nodes)
    no_latency_dist_vec, _ = topo_search(workflow, in_degree_vec.copy(), group_set, True)
    no_latency_crit_length = no_latency_dist_vec[workflow.end.name][0]

    while True:
        dist_vec, prev_vec = topo_search(workflow, in_degree_vec.copy(), group_set, False)
        topo_search_cnt = topo_search_cnt + 1
        crit_length = dist_vec[workflow.end.name][0]
        if crit_length < no_latency_crit_length * penalty_rate:
            break
        elif group_size == total_node_cnt:
            break
        crit_vec = dict()
        tmp_node_name = workflow.end.name
        while tmp_node_name != workflow.start.name:
            crit_vec[tmp_node_name] = prev_vec[tmp_node_name]
            tmp_node_name = prev_vec[tmp_node_name][0]
        crit_vec = sorted(crit_vec.items(), key=lambda c: c[1][1], reverse=True)
        if not merge_node(crit_vec, group_set, group_size):
            group_size = group_size + 1
            merge_node(crit_vec, group_set, group_size)

    group_detail = []
    for node_set in group_set:
        group_id = str(uuid.uuid4())
        for node in node_set:
            group_detail.append({'name': node, 'group_id': group_id, 'node_id': hash(group_id) % node_cnt})
    prerequisite = get_prerequisite(workflow)
    group_size = 1 if topo_search_cnt == 1 else group_size
    ratio = crit_length / no_latency_crit_length

    return json.dumps(group_detail), json.dumps(prerequisite)


detail, requisite = grouping('0', parser_with_time.mainObject)
print(detail)
print(requisite)
