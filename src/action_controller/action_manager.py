import gevent

repack_clean_interval = 5.000 # repack and clean every 5 seconds
dispatch_interval = 0.005 # 200 qps at most

# the class for scheduling actions' inter-operations
class ActionManager:
    def __init__(self, action_list):
        self.action_list = action_list

    def start_loop(self):
        gevent.spawn_later(repack_clean_interval, self._clean_loop)

    def _clean_loop(self):
        gevent.spawn_later(repack_clean_interval, self._clean_loop)
        for action in self.action_list:
            gevent.spawn(action.repack_and_clean)

    def _dispatch_loop(self):
        gevent.spawn_later(dispatch_interval, self._dispatch_loop)
        for action in self.action_list:
            gevent.spawn(action.dispatch_request)
