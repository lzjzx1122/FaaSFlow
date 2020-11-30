from ServerlessBase import ServerlessBase

class Function(ServerlessBase):
    def __init__(self, name, next, source, parameters):
        ServerlessBase.__init__(self, 'function', name, next)
        self.source = source
        self.parameters = parameters