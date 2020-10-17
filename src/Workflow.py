from ServerlessBase import ServerlessBase

class Workflow(ServerlessBase):
    def __init__(self, name, next, start, end, nodes):
        ServerlessBase.__init__(self, name, next)
        self.start = start
        self.end = end
        self.nodes = nodes