from ServerlessBase import ServerlessBase


class Function(ServerlessBase):
    def __init__(self, name, next, nextDis, source, parameters, runtime, input_files, output_files):
        ServerlessBase.__init__(self, 'function', name, next, nextDis)
        self.source = source
        self.parameters = parameters
        self.runtime = runtime
        self.input_files = input_files
        self.output_files = output_files
