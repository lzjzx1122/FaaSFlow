from ServerlessBase import ServerlessBase


class Function(ServerlessBase):
    def __init__(self, name, next, nextDis, source, parameters, runtime):
        ServerlessBase.__init__(self, 'function', name, next, nextDis)
        self.source = source
        self.parameters = parameters
        self.runtime = runtime
