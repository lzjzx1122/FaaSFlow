import os
import subprocess
import sys
import time
import uuid
import yaml
from typing import List

sys.path.append('../../')
from flask import Flask, request
from config import config

proxy = Flask(__name__)
processes = [None, None, None]


def sensitivity_set(cpu):
    file_path = '../../benchmark/templates_info.yaml'
    with open(file_path, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    for entry in data['templates']:
        if 'wordcount' in entry['template_name']:
            entry['cpus'] = cpu
    with open(file_path, 'w') as f:
        yaml.dump(data, f)


@proxy.route('/clear', methods=['post'])
def start():
    global processes
    for p in processes:
        if p is not None:
            p.kill()

    inp = request.get_json(force=True, silent=True)
    wc_cpu = 0.2
    if inp is not None:
        wc_cpu = inp['wc_cpu']
    sensitivity_set(wc_cpu)

    os.system('docker rm -f $(docker ps -aq)')
    os.system('service docker restart')
    os.system('docker run -itd -p 6379:6379 --name redis redis')
    time.sleep(5)
    processes[0] = subprocess.Popen(['python3', 'proxy.py', addr, '8000'])
    time.sleep(20)
    processes[1] = subprocess.Popen(['python3', 'disk_reader.py'])
    processes[2] = subprocess.Popen(['python3', 'prefetcher.py'])
    time.sleep(1)
    return 'OK', 200


if __name__ == '__main__':
    addr = sys.argv[1]
    proxy.run('0.0.0.0', 7999, threaded=True)
