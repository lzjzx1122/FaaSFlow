from gevent import monkey
monkey.patch_all()
import docker
import couchdb
import sys
import json
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from action import Action
from port_manager import PortManager
from action_manager import ActionManager
import time

proxy = Flask(__name__)
proxy.debug = False
action = None
#port_manager = None #TODO
#action_manager = None #TODO
server = None

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = 'http://127.0.0.1:5984/'
db_name = 'action_results'

@proxy.route('/init', methods=['POST'])
def init():
    global action
    data = request.get_json(force=True, silent=True)
    #print ("init :", data['action'], ' ', data['min_port'], ' ', data['max_container'])
    
    db_server = couchdb.Server(couchdb_url)
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    action = Action(docker.from_env(),
                    data['action'],
                    data['pwd'],
                    PortManager(data['min_port'], data['min_port'] + data['max_container']),
                    ActionManager(),
                    db,
                    data['QOS_time'],
                    data['QOS_requirement'],
                    data['max_container'])
    return ('OK', 200)

@proxy.route('/repack', methods=['POST'])
def repack():
    action.remove_lender()
    return ('OK', 200)

@proxy.route('/run', methods=['POST'])
def run():
    data = request.get_json(force=True, silent=True)
    if action == None:
        return ('NO', 404)
    action.send_request(data['request_id'], data['data'])
    return ('OK', 200)

@proxy.route('/lend', methods=['GET'])
def lend():
    res = action.giveout_container()
    if res is None:
        return ('no lender', 404)
    else:
        return (json.dumps({"id": res[0], "port": res[1]}), 200)

@proxy.route('/status', methods=['GET'])
def status():
    return action.pool_status()

@proxy.route('/end', methods=['POST'])
def end():
    action.end()
    global server
    server.stop()
    return ('OK', 200)

def main():
    global server
    server = WSGIServer(('0.0.0.0', int(sys.argv[1])), proxy)
    server.serve_forever()

if __name__ == '__main__':
    main()
