import proxy
import docker
import couchdb
from action import Action

class TestPortManager:
    def __init__(self, min_port, max_port):
        self.port_resource = list(range(min_port, max_port))

    def get(self):
        return self.port_resource.pop(0)

    def put(self, port):
        self.port_resource.append(port)

class TestActionManager:
    def rent(self, action_name):
        return None

    def create_pack_image(self, action_name):
        return 'action_linpack_repack'

    def no_lender(self, action_name):
        pass

    def have_lender(self, action_name):
        pass

db_server = couchdb.Server(proxy.couchdb_url)
if proxy.db_name in db_server:
    db_server.delete(proxy.db_name)
db = db_server.create(proxy.db_name)

client = docker.from_env()
for c in client.containers.list(filters={'ancestor': 'action_linpack'}):
    c.remove(force=True)

for c in client.containers.list(filters={'ancestor': 'action_linpack_repack'}):
    c.remove(force=True)

proxy.action = Action(client,
                      'linpack',
                      'linpack',
                      TestPortManager(30000, 310000),
                      TestActionManager(),
                      db,
                      0.3,
                      0.95,
                      10)

app = proxy.proxy
print('ok')
proxy.main()
