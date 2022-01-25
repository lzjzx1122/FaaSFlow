import subprocess
import time
import psutil
import grouping
import pandas as pd

if __name__ == '__main__':
    node_cnts = [10, 25, 50, 100, 200]
    mem = []
    cpu = []
    for node_cnt in node_cnts:
        print('running workflow with {} nodes'.format(node_cnt))
        ret = subprocess.Popen(['python3', 'grouping.py', str(node_cnt)])
        manager = psutil.Process(ret.pid)
        mem_percent = 0
        cpu_percent = 0
        cnt = 0
        while ret.poll() is None:
            c = manager.cpu_percent(interval=0.01)
            mem_percent = max(mem_percent, manager.memory_percent())
            cpu_percent = cpu_percent + c
            cnt = cnt + 1
        cpu_percent /= cnt
        start = time.time()
        grouping.main(node_cnt)
        end = time.time()
        mem_mb = mem_percent * 61.9 * 1024 * 0.01
        cpu_core_time = cpu_percent * 0.01 * (end - start)
        mem.append(mem_mb)
        cpu.append(cpu_core_time)
    pd.DataFrame({'node': node_cnts, 'core x second': cpu, 'mem_usage': mem}).to_csv('scheduler_scalability.csv')