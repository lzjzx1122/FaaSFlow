from ServerlessBase import ServerlessBase

class Function(ServerlessBase):
    def __init__(self, name, next, operation, parameters):
        ServerlessBase.__init__(self, name, next)
        self.operation = operation
        self.parameters = parameters