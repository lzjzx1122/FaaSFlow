from ServerlessBase import ServerlessBase

class Switch(ServerlessBase):
    def __init__(self, name, next, choices):
        ServerlessBase.__init__(self, name, next)
        self.choices = choices