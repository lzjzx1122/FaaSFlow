from gevent import monkey
monkey.patch_all()
import sys
from proxy import ProxyServer
from gevent.pywsgi import WSGIServer
from port_manager import PortManager
from action_info import parse

def main():
    port_manager = PortManager(20000, 30000)
    action_info = parse(sys.argv[2])
    app = ProxyServer(action_info, port_manager)
    app.action_manager.start_loop()
    server = WSGIServer(('0.0.0.0', int(sys.argv[1])), app.wsgi_app)
    server.serve_forever()

if __name__ == '__main__':
    main()