import yaml

# data structure for action info
class ActionInfo:
    def __init__(self, action_name, pwd, img_name, max_container, qos_time, qos_requirement):
        self.action_name = action_name
        self.pwd = pwd
        self.img_name = img_name
        self.max_container = max_container
        self.qos_time = qos_time
        self.qos_requirement = qos_requirement

def parse(action_config):
    action_info = []
    with open(action_config, 'r') as f:
        config = yaml.safe_load(f)
        max_container = config['max_container']
        for c in config['actions']:
            info = ActionInfo(c['name'],
                              c['pwd'],
                              c['image'],
                              max_container,
                              float(c['qos_time']),
                              float(c['qos_requirement']))
            action_info.append(info)
    return action_info


