import os.path

import yaml


class TemplateInfo:
    def __init__(self, template_name, image_name, blocks: dict, cpus, gc, max_containers=1000):
        self.template_name = template_name
        self.image_name = image_name
        self.blocks = blocks
        self.cpus = cpus
        self.gc = gc
        self.max_containers = max_containers

    @classmethod
    def parse(cls, config_path):
        templates_info = []
        config_file = os.path.join(config_path, 'templates_info.yaml')
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
            for func in data['templates']:
                template_name = func['template_name']
                print(template_name)
                image_name = func['image_name']
                blocks = func['blocks']
                cpus = func['cpus']
                gc = False
                if 'gc' in func:
                    gc = func['gc']
                templates_info.append(cls(template_name, image_name, blocks, cpus, gc))
        return templates_info
