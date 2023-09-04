import json
import socket

import sys
import socketserver

sys.path.append('../../')
import os.path
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from config import config

prefetch_dir = config.PREFETCH_POOL_PATH
app = Flask(__name__)


# @app.route('/fetch_from_disk', methods=['GET'])
# def fetch_disk_data():
#     inp = request.get_json(force=True, silent=True)
#     filename = inp['db_key']
#     filepath = os.path.expanduser('~/CodeLess/benchmark/template_functions/video__upload/test.mp4')
#     data = None
#     with open(filepath, 'rb') as f:
#         data = f.read()
#     print(len(data))
#     return data

class MyServer(socketserver.BaseRequestHandler):
    """
    必须继承socketserver.BaseRequestHandler类
    """

    def handle(self):
        """
        必须实现这个方法！
        :return:
        """
        conn = self.request  # request里封装了所有请求的数据
        request_info = conn.recv(64 * 1024)
        filename = json.loads(request_info)['db_key']
        filepath = os.path.join(prefetch_dir, filename)
        # filepath = os.path.expanduser('~/CodeLess/benchmark/template_functions/video__upload/test.mp4')
        with open(filepath, 'rb') as f:
            conn.sendfile(f)
        conn.close()


# def message_handle(client: socket.socket):
#     request_info = client.recv(64 * 1024)
#     filename = json.loads(request_info)['db_key']
#     filepath = os.path.join(prefetch_dir, filename)
#     # filepath = os.path.expanduser('~/CodeLess/benchmark/template_functions/video__upload/test.mp4')
#     with open(filepath, 'rb') as f:
#         client.sendfile(f)
#     client.close()
#     pass


if __name__ == '__main__':
    sock_path = os.path.join(config.FILE_CONTROLLER_PATH, 'transfer.sock')
    if os.path.exists(sock_path):
        os.unlink(sock_path)
    server = socketserver.ThreadingUnixStreamServer(sock_path, MyServer)
    server.serve_forever()
    # server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    #
    # if os.path.exists(sock_path):
    #     os.unlink(sock_path)
    # server.bind(sock_path)
    # server.listen(1000)
    # while True:
    #     connection, address = server.accept()
    #     message_handle(connection)
    #
    #
    # server = WSGIServer(('0.0.0.0', 8001), app)
    # server.serve_forever()
