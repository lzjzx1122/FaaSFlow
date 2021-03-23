import yaml
import os

# data structure for function info
class FunctionInfo:
    def __init__(self, function_name, max_containers, qos_time, qos_requirement):
        self.function_name = function_name
        self.max_containers = max_containers
        self.qos_time = qos_time
        self.qos_requirement = qos_requirement

def generate_image(config_path, function_name, packages):
    dockerfile_path = os.path.join(config_path, function_name, "Dockerfile")
    requirements = ""
    for package in packages:
        requirements += " " + package
    with open(dockerfile_path, "w") as f:
        f.write("FROM workflow_base\n")
        if requirements != "":
            f.write("RUN pip3 --no-cache-dir install{}".format(requirements))
    os.system("cd {} && docker build --no-cache -t {}_image .".format(dockerfile_path, function_name))

def parse(config_path):
    function_info = []
    config_file = os.path.join(config_path, "function_info.yaml")
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
        for c in config['functions']:
            print("c", c)
            function_name = c['name']
            packages = c['packages'] if 'packages' in c else [] 
            generate_image(config_path, function_name, packages)
            info = FunctionInfo(function_name,
                              c['max_containers'],
                              float(c['qos_time']),
                              float(c['qos_requirement']))
            function_info.append(info)
    return function_info