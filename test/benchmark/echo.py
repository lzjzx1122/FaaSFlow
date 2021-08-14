import time
import json
import sys
from flask import Flask
from gevent.pywsgi import WSGIServer
app = Flask(__name__)


@app.route('/echo', methods = ['POST'])
def echo():
    return json.dumps({'status': 'ok'})

if __name__ == '__main__':
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()