from typing import List, Dict
import gevent
import os
import docker
from src.function_manager.template import Template
from src.function_manager.template_info import TemplateInfo
from src.function_manager.port_manager import PortManager

dispatch_interval = 0.003
regular_clean_interval = 5.000


class FunctionManager:
    def __init__(self, min_port, config_path):
        self.templates_info = TemplateInfo.parse(config_path)
        self.port_manager = PortManager(min_port, min_port + 5000)
        self.client = docker.from_env()
        self.templates: Dict[str, Template] = {
            template_info.template_name: Template(self.client, template_info, self.port_manager,
                                                  len(template_info.blocks), template_info.cpus)
            for template_info in self.templates_info
        }
        self.init()

    def init(self):
        print('Clearing previous containers...')
        os.system('docker rm -f $(docker ps -aq --filter label=workflow)')
        gevent.spawn_later(dispatch_interval, self.dispatch_event)
        gevent.spawn_later(regular_clean_interval, self.regular_clean_event)

    def dispatch_event(self):
        gevent.spawn_later(dispatch_interval, self.dispatch_event)
        for func in self.templates.values():
            gevent.spawn(func.dispatch_request)

    def regular_clean_event(self):
        gevent.spawn_later(regular_clean_interval, self.regular_clean_event)
        for func in self.templates.values():
            gevent.spawn(func.regular_clean)

    def allocate(self, request_id, workflow_name, function_name, function_info):
        self.templates[function_name].allocate(request_id, workflow_name, function_name, function_info)

    def send_data(self, request_id, workflow_name, function_name, datas, datatype):
        self.templates[function_name].send_data(request_id, workflow_name, function_name, datas, datatype)

    def allocate_block(self, request_id, workflow_name, template_name, templates_infos, block_name, block_inputs: dict,
                       block_infos):
        assert template_name in self.templates
        self.templates[template_name].allocate_block(request_id, workflow_name, template_name, templates_infos,
                                                     block_name, block_inputs, block_infos)

    def preempt_block(self, request_id, workflow_name, template_name, buddy_block_name, block_name, block_inputs,
                      block_infos):
        return self.templates[template_name].preempt_block(request_id, workflow_name, template_name, buddy_block_name,
                                                           block_name, block_inputs, block_infos)
        pass
