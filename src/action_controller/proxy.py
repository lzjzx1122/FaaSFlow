from gevent import monkey
monkey.patch_all()
import docker
import couchdb
import sys
from flask import Flask, request
from action import Action

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = 'http://127.0.0.1:5984/'
db_name = 'action_results'

def init(action_infos, port_manager):
    db_server = couchdb.Server(couchdb_url)
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    client = docker.from_env()
    actions = {x.action_name: Action(client, db, x, port_manager) for x in action_infos}

    app = Flask('action-controller')
    
    @app.route('/run/<action_name>', methods=['POST'])
    def run(action_name):
        data = request.get_json(force=True, silent=True)
        if action_name not in actions:
            return ('NO', 404)
        actions[action_name].send_request(data['request_id'], data['data'])
        return ('OK', 200)

    @app.route('/status', methods=['GET'])
    def status():
        return {it: it.get_status() for it in actions}

    @app.route('/end', methods=['POST'])
    def end():
        # TODO
        return ('OK', 200)

    return app
