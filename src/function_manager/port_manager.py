class PortManager:
    def __init__(self, min_port, max_port):
        self.port_list = list(range(min_port, max_port))

    def allocate(self):
        if len(self.port_list) == 0:
            raise Exception('No available port!')
        return self.port_list.pop(0)

    def put(self, port):
        self.port_list.append(port)
