from ServerlessBase import ServerlessBase

class Workflow(ServerlessBase):
    def __init__(self, name, next, nextDis, start, end, nodes):
        ServerlessBase.__init__(self, 'workflow', name, next, nextDis)
        self.start = start
        self.end = end
        self.nodes = nodes