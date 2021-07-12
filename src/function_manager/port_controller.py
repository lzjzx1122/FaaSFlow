# a really simple port controller allocating port in a range
class PortController:
    def __init__(self, min_port, max_port):
        self.port_resource = list(range(min_port, max_port))

    def get(self):
        if len(self.port_resource) == 0:
            raise Exception("no idle port")
        return self.port_resource.pop(0)

    def put(self, port):
        self.port_resource.append(port)
