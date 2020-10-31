import docker
import couchdb
import gevent
from flask import Flask, request
from action import Action
from action_manager import ActionManager

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = f'http://{username}:{password}@127.0.0.1:5984/'
db_name = 'action_results'

class ProxyServer:
    def __init__(self, action_info, port_manager):
        self.db_server = couchdb.Server(couchdb_url)
        if db_name in self.db_server:
            db = self.db_server[db_name]
        else:
            db = self.db_server.create(db_name)

        client = docker.from_env()
        self.actions = {x.action_name: Action(client, db, x, port_manager) for x in action_info}
        self.action_manager = ActionManager(self.actions)

        self.wsgi_app = Flask('action-controller')
        self.wsgi_app.add_url_rule('/run/<action_name>', '', self.run, methods=['POST'])
        self.wsgi_app.add_url_rule('/status', '', self.status, methods=['GET'])
        self.wsgi_app.add_url_rule('/end', '', self.end, methods=['POST'])

    def run(self, action_name):
        data = request.get_json(force=True, silent=True)
        if action_name not in self.actions:
            return ('NO', 404)
        self.actions[action_name].send_request(data['request_id'], data['data'])
        return ('OK', 200)

    def status(self):
        return {it: it.get_status() for it in self.actions}

    def end(self):
        # TODO
        return ('OK', 200)
