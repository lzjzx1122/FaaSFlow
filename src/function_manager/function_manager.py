import gevent
import couchdb
import docker
import os
from function_info import parse
from port_controller import PortController
from function import Function

repack_clean_interval = 5.000 # repack and clean every 5 seconds
dispatch_interval = 0.005 # 200 qps at most

username = 'openwhisk'
password = 'openwhisk'
couchdb_url = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
db_name = 'results'

# the class for scheduling functions' inter-operations
class FunctionManager:
    def __init__(self, config_path):
        self.function_info = parse(config_path)
        self.db_server = couchdb.Server(couchdb_url)
        db = self.db_server[db_name]
        #os.system("curl -X DELETE " + couchdb_url + db_name)
        #if db_name in self.db_server:
        # self.db_server.delete(db_name)

        self.port_controller = PortController(10080, 30000)
        self.client = docker.from_env()

        self.functions = {x.function_name: Function(self.client, db, x, self.port_controller, x.function_name) for x in self.function_info}

        self.init()
       
    def init(self):
        print("Clearing previous containers.")
        os.system('docker rm -f $(docker ps -aq --filter ancestor=workflow_base)')

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
    
    def run(self, function_name, request_id, runtime, input, output, to, keys):
        print('run', function_name, request_id, runtime, input, output, to, keys)
        if function_name not in self.functions:
            raise Exception("No such function!")
        return self.functions[function_name].send_request(request_id, runtime, input, output, to, keys)
