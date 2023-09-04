from typing import Dict


# this information is different per request
class RequestInfo:
    def __init__(self, workflow_name, ips: set, templates_infos: Dict[str, dict]):
        # This request will cover how many nodes, it is useful for delete already finished RequestInfo in each node
        # after last function finished.
        self.workflow_name = workflow_name
        self.ips = ips
        self.templates_infos = templates_infos  # including the pre-allocate IP address of each function
        self.templates_infos['VIRTUAL'] = {'ip': '127.0.0.1'}
