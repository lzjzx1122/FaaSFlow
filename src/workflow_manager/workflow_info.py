import os.path
from typing import Dict

import yaml


# this information is different per workflow
class WorkflowInfo:
    def __init__(self, workflow_name, templates_infos, raw_data):
        self.workflow_name = workflow_name
        self.templates_infos = templates_infos
        self.data = raw_data

    @classmethod
    def parse(cls, config_dict):
        workflows_info = {}
        for path in config_dict.values():
            config_file = os.path.join(path, 'workflow_info.yaml')
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
            print(data)
            workflow_name = data['workflow_name']
            # datas_successors = {}
            # functions_predecessors = {}
            templates_infos = {}
            # user_input_src_infos = {}
            # templates_blocks_predecessor_cnt = {}
            # for template_name, template_infos in data['templates'].items():
            #     templates_infos[template_name] = template_infos
            #     templates_blocks_predecessor_cnt[template_name] = {}
            #     for block_name, block_infos in template_infos['blocks'].items():
            #         templates_blocks_predecessor_cnt[template_name][block_name] = 0
            # for global_input_name, global_input_infos in data['global_inputs'].items():
            #     for dest_template_name, dest_template_infos in global_input_infos['dest'].items():
            #         if dest_template_name == '$USER':
            #             pass
            #         else:
            #             for dest_block_name, dest_block_infos in dest_template_infos.items():
            #                 for dest_input_name in dest_block_infos:
            #                     templates_blocks_predecessor_cnt[dest_template_name][dest_block_name] += 1
            for template_name, template_infos in data['templates'].items():
                templates_infos[template_name] = template_infos
                if template_name == 'VIRTUAL':
                    # Todo: What is for virtual?
                    continue
                for block_name, block_infos in template_infos['blocks'].items():
                    for input_name, input_infos in block_infos['input_datas'].items():
                        if input_infos['type'] == 'NORMAL':
                            pass
                        elif input_infos['type'] == 'LIST':
                            pass
                        else:
                            raise Exception('undefined input type: ', input_infos['type'])
                    for output_name, output_infos in block_infos['output_datas'].items():
                        if output_infos['type'] == 'NORMAL':
                            pass
                            # for dest_template_name, dest_template_infos in output_infos['dest'].items():
                            #     if dest_template_name == '$USER':
                            #         pass
                            #     else:
                            #         for dest_block_name, dest_block_infos in dest_template_infos.items():
                            #             for dest_input_name in dest_block_infos:
                            #                 dest_input_type = \
                            #                     data['templates'][dest_template_name]['blocks'][dest_block_name][
                            #                         'input_datas'][dest_input_name]['type']
                            #                 if dest_input_type == 'NORMAL':
                            #                     pass
                            #                 elif dest_input_type == 'LIST':
                            #                     pass
                            #                 else:
                            #                     raise Exception('undefined input type: ', dest_input_type)
                        elif output_infos['type'] == 'FOREACH':
                            pass
                        elif output_infos['type'] == 'MERGE':
                            pass
                        else:
                            raise Exception('undefined output type: ', output_infos['type'])

            workflows_info[workflow_name] = cls(workflow_name, templates_infos, data)
        return workflows_info


# def parse(config_dict: dict):
#     workflows_info = {}
#     for path in config_dict.values():
#         config_file = os.path.join(path, 'workflow_info.yaml')
#         with open(config_file, 'r') as f:
#             data = yaml.safe_load(f)
#         print(data)
#         workflow_name = data['workflow_name']
#         # datas_successors = {}
#         # functions_predecessors = {}
#         templates_infos = {}
#         # user_input_src_infos = {}
#         templates_blocks_predecessor_cnt = {}
#         for template_name, template_infos in data['templates'].items():
#             templates_infos[template_name] = template_infos
#             templates_blocks_predecessor_cnt[template_name] = {}
#             for block_name, block_infos in template_infos['blocks'].items():
#                 templates_blocks_predecessor_cnt[template_name][block_name] = 0
#         for template_name, template_infos in data['templates'].items():
#             for block_name, block_infos in template_infos['blocks'].items():
#                 for output_name, output_infos in block_infos['output_datas'].items():
#                     if output_infos['type'] == 'NORMAL':
#                         for dest_template_name, dest_template_infos in output_infos['dest']:
#                             if dest_template_name == '$USER':
#                                 pass
#                             else:
#                                 for dest_block_name, dest_block_infos in dest_template_infos:
#                                     for dest_input_name in dest_block_infos:
#                                         dest_input_type = \
#                                             data['templates'][dest_template_name]['blocks'][dest_block_name][
#                                                 'input_datas'][dest_input_name]['type']
#                                         templates_blocks_predecessor_cnt[dest_template_name][dest_block_name] += 1
#                                         if dest_input_type == 'NORMAL':
#                                             pass
#                                         elif dest_input_type == 'LIST':
#                                             pass
#                                         else:
#                                             raise Exception('undefined input type: ', dest_input_type)
#                     else:
#                         raise Exception('undefined output type: ', output_infos['type'])
#
#         # function_name = template['name']
#         # functions_infos[function_name] = func
#         # functions_predecessors[function_name] = []
#         # input_datas: dict = func['input_datas']
#         # for parameter, info in input_datas.items():
#         #     src = []
#         #     if info['type'] == 'NORMAL':
#         #         src.append(info['src'])
#         #     elif info['type'] == 'LIST':
#         #         src = info['src']
#         #     for input_data in src:
#         #         if '$USER' in input_data:
#         #             if input_data not in user_input_src_infos:
#         #                 user_input_src_infos[input_data] = []
#         #             user_input_src_infos[input_data].append(function_name)
#         #         if input_data not in datas_successors:
#         #             datas_successors[input_data] = []
#         #         datas_successors[input_data].append(function_name)
#         #         functions_predecessors[function_name].append(input_data)
#         workflows_info[workflow_name] = WorkflowInfo(workflow_name, templates_infos, templates_blocks_predecessor_cnt,
#                                                      data)
#     return workflows_info

# a = WorkflowInfo.parse({'': '../../benchmark/file_processing'})
# print(a)
