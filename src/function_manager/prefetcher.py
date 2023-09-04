import os.path
import shutil

import gevent.event


class Prefetcher:
    def __init__(self):
        self.requests_keys_status = {}
        pass


    def init(self, prefetch_dir):
        if os.path.exists(prefetch_dir):
            shutil.rmtree(prefetch_dir)
        os.mkdir(prefetch_dir)
        os.chmod(prefetch_dir, 0o777)


prefetcher = Prefetcher()
