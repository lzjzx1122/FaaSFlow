import psutil
import sys
import getopt

def analyze(pid):
    manager = psutil.Process(pid)
    mem_percent = manager.memory_percent()
    cpu_percent = manager.cpu_percent(interval=1)
    mem_mb = mem_percent * 61.9 * 1024 * 0.01
    cpu_core = cpu_percent * 0.01
    with open("component_overhead.txt", 'w') as f:
        f.write(f'mem_usage: {mem_mb} MB\n')
        f.write(f'cpu_usage: {cpu_core} core\n')

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],'',['pid='])
    for name, value in opts:
        if name == '--pid':
            pid = value
    analyze(int(pid))
