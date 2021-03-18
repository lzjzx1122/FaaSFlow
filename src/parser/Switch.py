from ServerlessBase import ServerlessBase

class Switch(ServerlessBase):
    def __init__(self, name, next, nextDis, choices):
        ServerlessBase.__init__(self, 'switch', name, next, nextDis)
        self.choices = choices