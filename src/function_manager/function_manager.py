import gevent
import couchdb
from function_info import parse

repack_clean_interval = 5.000 # repack and clean every 5 seconds
dispatch_interval = 0.005 # 200 qps at most

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = f'http://{username}:{password}@127.0.0.1:5984/'
db_name = 'results'

# the class for scheduling functions' inter-operations
class FunctionManager:
    def __init__(self, config_path):
        self.function_info = parse(config_path)
        self.db_server = couchdb.Server(couchdb_url)
        if db_name in self.db_server:
            db = self.db_server[db_name]
        else:
            db = self.db_server.create(db_name)

        self.port_manager = PortManager(20000, 30000)
        self.client = docker.from_env()

        self.functions = {x.function_name: Function(client, db, x, port_manager) for x in self.function_info}
       
    def init(self):
        gevent.spawn_later(repack_clean_interval, self._clean_loop)
        gevent.spawn_later(dispatch_interval, self._dispatch_loop)
    
    def _clean_loop(self):
        gevent.spawn_later(repack_clean_interval, self._clean_loop)
        for function in self.functions.values():
            gevent.spawn(function.repack_and_clean)

    def _dispatch_loop(self):
        gevent.spawn_later(dispatch_interval, self._dispatch_loop)
        for function in self.functions.values():
            gevent.spawn(function.dispatch_request)
    
    def run(self, function_name, request_id, parameters):
        if function_name not in self.functions:
            raise Exception("No such function!")
        self.functions[function_name].send_request(request_id, parameters)

manager = FunctionManager("actions")