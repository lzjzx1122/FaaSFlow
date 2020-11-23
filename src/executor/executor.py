import gevent
import rejson
from rejson import Path
from schedule import grouping, schedule

cluster = None
db = None

# do the preparation job:
#   1. connecting to database
def init():
    global db
    db = rejson.Client(host='localhost', port=6379, decode_responses=True)

# do the preparation job for a request before calling run()
# workflow is a Workflow obj
def init_req(req_id, workflow):
    # create a record in database
    create_record(req_id)
    # grouping and scheduling use database as store, so nothing retured
    grouping(req_id, workflow)

# node is a Function or Switch obj
# node_state is a map from node's name to a gevent.event.Event or None
def run(req_id, node, node_state):
    # wait for the previous nodes
    gevent.wait([node_state[n.name] for n in node.prev])

    # run the node
    if node.type == 'workflow':
        runWorkflow(req_id, node)
    elif node.type == 'function':
        runFunction(req_id, node)
    elif node.type == 'switch':
        runSwitch(req_id, node)

    # notify next node
    node_state[node.name].set()

# workflow is a Workflow obj
def runWorkflow(req_id, workflow):
    node_state = {}
    for node in workflow.nodes:
        node_state[node.name] = gevent.event.Event()
    for node in workflow.nodes:
        gevent.spawn(run, req_id, node, node_state)
    node_state[node.end.name].wait()

# node is a Function obj
def runFunction(req_id, node):
    # get the parameters of node
    params = {}
    for k, v in node.parameters.items():
        if type(v) is str and '$' in v:
            params[k] = get_data(req_id, v)
        else:
            params[k] = v

    machine = schedule(req_id, node)
    res = cluster.send(machine, node, params)
    put_node_result(req_id, node.name, res)

# node is a Swirch obj
def runSwitch(req_id, node):
    # node.choices should be a list of (cond, go) tuples
    # TODO: need to be changed in parser
    for cond, next_node in node.choices:
        if cond == 'default' or eval_cond(req_id, cond):
            if node.type == 'workflow':
                runWorkflow(req_id, next_node)
            elif node.type == 'function':
                runFunction(req_id, next_node)
            elif node.type == 'switch':
                runSwitch(req_id, next_node)
            break

symbols = ['<=', '>=', '==', '<', '>']
def eval_cond(req_id, cond):
    # TODO: currently support int data only
    for s in symbols:
        if s in cond:
            left, right = cond.split(s)
            left = left.strip()
            right = right.strip()
            left_number = get_data(req_id, left) if '$' in left else int(left)
            right_number = get_data(req_id, right) if '$' in right else int(right)
            if s == '<=':
                return left_number <= right_number
            elif s == '>=':
                return left_number >= right_number
            elif s == '==':
                return left_number == right_number
            elif s == '<':
                return left_number < right_number
            elif s == '>':
                return left_number > right_number
    return True

## Currently using RedisJson as storage database
# create a record in redis for a request
def create_record(req_id):
    record = {
        "id": req_id,
        "Output": {}
    }
    db.jsonset(req_id, Path.rootPath(), record)

# put a action's result into database
def put_node_result(req_id, name, data):
    path = '.Output.' + name
    db.jsonset(req_id, Path(path), data)

# path is a string of JsonPath
def get_data(req_id, path):
    return db.jsonget(req_id, Path(path))
