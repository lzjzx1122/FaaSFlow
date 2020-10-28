import sys
import proxy
from gevent.pywsgi import WSGIServer
from port_manager import PortManager
from action_info import parse

def main():
    port_manager = PortManager(20000, 30000)
    action_info = parse(sys.argv[2])
    app = proxy.init(action_info, port_manager)
    server = WSGIServer(('0.0.0.0', int(sys.argv[1])), app)
    server.serve_forever()

if __name__ == '__main__':
    main()