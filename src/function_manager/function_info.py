import yaml
import os

# data structure for function info
class FunctionInfo:
    def __init__(self, workflow_name, function_name, img_name, max_containers, qos_time, qos_requirement):
        self.workflow_name = workflow_name
        self.function_name = function_name
        self.img_name = img_name
        self.max_containers = max_containers
        self.qos_time = qos_time
        self.qos_requirement = qos_requirement

def generate_image(config_path, function_name, packages):
    function_path = os.path.join(config_path, function_name)
    dockerfile_path = os.path.join(function_path, "Dockerfile")
    requirements = ""
    for package in packages:
        requirements += " " + package
    with open(dockerfile_path, "w") as f:
        f.write("FROM workflow_base\n")
        f.write('COPY main.py /exec/main.py\n')
        if requirements != "":
            f.write("RUN pip3 --no-cache-dir install{}".format(requirements))
    os.system("cd {} && docker build --no-cache -t image_{} .".format(function_path, function_name))

# get all functions' infomations from configuration file
def parse(config_path):
    function_info = []
    config_file = os.path.join(config_path, "function_info.yaml")
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
        workflow_name = config['workflow']
        max_containers = config['max_containers']
        for c in config['functions']:
            function_name = c['name']
            img_name = c['image']
            
            # clear previous containers.
            # print("Clearing previous containers.")
            # os.system('docker stop $(docker ps -a | grep \"' + 'image_' + function_name + '\" | awk \'{print $1}\')')
            # os.system('docker rm $(docker ps -a | grep \"' + 'image_' + function_name  + '\" | awk \'{print $1}\')')

            # print("generate:", function_name)
            # packages = c['packages'] if 'packages' in c else [] 
            #generate_image(config_path, function_name, packages)
            
            info = FunctionInfo(workflow_name, function_name,
                              img_name,
                              int(max_containers),
                              float(c['qos_time']),
                              float(c['qos_requirement']))
            print('img_name', info.img_name)
            function_info.append(info)
    return function_info
