class function:
    def __init__(self, name, prev, next, nextDis, source, runtime, input_files, output_files, conditions):
        self.name = name
        self.prev = prev
        self.next = next
        self.nextDis = nextDis
        self.source = source
        self.runtime = runtime
        self.input_files = input_files
        self.output_files = output_files
        self.conditions = conditions


class workflow:
    def __init__(self, start_functions, nodes, global_input, total, parent_cnt, foreach_functions, merge_functions):
        self.start_functions = start_functions
        self.nodes = nodes  # dict: {name: function()}
        self.global_input = global_input
        self.total = total
        self.parent_cnt = parent_cnt  # dict: {name: parent_cnt}
        self.foreach_functions = foreach_functions
        self.merge_functions = merge_functions