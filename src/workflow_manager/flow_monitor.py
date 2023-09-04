import os
import queue
import shutil
import time
import redis
import couchdb
from gevent.lock import BoundedSemaphore
import gevent
from config import config
from typing import Dict
from src.workflow_manager.repository import Repository
repo = Repository()
dispatch_interval = 0.1

prefetch_dir = config.PREFETCH_POOL_PATH


class DataInfo:
    def __init__(self, request_id, key, expire_time, local_cnt, in_redis, in_disk, in_couchDB, datasize):
        self.key = key
        self.expire_time = expire_time
        self.in_redis = in_redis
        self.in_disk = in_disk
        self.in_couchDB = in_couchDB
        self.request_id = request_id
        self.dependencies_cnt = local_cnt
        self.link_mnts = []
        self.status = None
        self.lock = BoundedSemaphore()
        self.born_time = time.time()
        self.datasize = datasize

    def __lt__(self, other: 'DataInfo'):
        return self.expire_time < other.expire_time


class FlowMonitor:
    def __init__(self):
        self.waiting_delete_keys = []
        self.expire_queue = queue.PriorityQueue()
        # Todo: this need GC.
        self.requests_keys_info: Dict[str, Dict[str, DataInfo]] = {}
        self.redis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        self.couchDB = couchdb.Server(config.COUCHDB_URL)['results']
        self.redis.flushall()
        gevent.spawn_later(dispatch_interval, self.regular_expire)

    def upload_all_logs(self):
        repo.upload_waiting_logs()

    def replicate_to_couchDB(self, request_id, key, val):
        datatype = None
        if key[-4:] == 'json':
            datatype = 'json'
        else:
            datatype = 'octet'
        while True:
            try:
                self.couchDB.put_attachment(self.couchDB[request_id], val, filename=key,
                                            content_type='application/' + datatype)
                break
            except Exception:
                pass

    def transfer_to_disk(self, datainfo: DataInfo):
        # Todo: use chunk size? However, if it needs to upload to couchdb, still need to fetch again
        key = datainfo.key
        val = self.redis[key]
        prefetch_filepath = os.path.join(prefetch_dir, key)
        with open(prefetch_filepath, 'wb') as f:
            f.write(val)
        if datainfo.dependencies_cnt == 0:
            self.remove_disk_key(datainfo)
            return
        datainfo.in_disk = True
        if not datainfo.in_couchDB:
            pass
            # gevent.spawn(self.replicate_to_couchDB, datainfo.request_id, key, val)
        # for mnt_path in datainfo.link_mnts:
        #     shutil.copy(prefetch_filepath, os.path.join(mnt_path, key))

    # Todo: potential problem: a disk key may be removed twice.
    def remove_disk_key(self, datainfo: DataInfo):
        key = datainfo.key
        prefetch_filepath = os.path.join(prefetch_dir, key)
        try:
            os.remove(prefetch_filepath)
        except Exception:
            pass

    def remove_redis_key(self, datainfo: DataInfo):
        key = datainfo.key
        while key in self.redis:
            try:
                # Todo: It should be write to disk!
                if datainfo.dependencies_cnt > 0 and not datainfo.in_disk:
                    self.transfer_to_disk(datainfo)
                datainfo.in_redis = False

                self.waiting_delete_keys.append(key)
                break

                self.redis.delete(key)
            except Exception:
                gevent.sleep(0.05)
        repo.save_redis_log(datainfo.request_id, datainfo.datasize, time.time() - datainfo.born_time)


    def regular_expire(self):
        gevent.spawn_later(dispatch_interval, self.regular_expire)
        if len(self.waiting_delete_keys) > 10:
            tmp = self.waiting_delete_keys
            self.waiting_delete_keys = []
            self.redis.delete(*tmp)
        while not self.expire_queue.empty() and self.expire_queue.queue[0].expire_time < time.time():
            datainfo: DataInfo = self.expire_queue.get()
            # datainfo.lock.acquire()
            if datainfo.status != 'removing_redis':
                datainfo.status = 'removing_redis'
                # datainfo.lock.release()
                # print('remove redis key passively:', datainfo.key)
                gevent.spawn(self.remove_redis_key, datainfo)
            else:
                pass
                # datainfo.lock.release()

    def decrease_key_dependencies(self, request_id, key):
        datainfo = self.requests_keys_info[request_id][key]
        datainfo.dependencies_cnt -= 1
        assert datainfo.dependencies_cnt >= 0
        if datainfo.dependencies_cnt == 0:
            # datainfo.lock.acquire()
            if datainfo.in_redis and datainfo.status != 'removing_redis':
                datainfo.status = 'removing_redis'
                # datainfo.lock.release()
                # print('remove redis key actively:', key)
                gevent.spawn(self.remove_redis_key, datainfo)
            else:
                pass
                # datainfo.lock.release()
            if datainfo.in_disk:
                # print('remove disk key actively:', key)
                gevent.spawn(self.remove_disk_key, datainfo)

    def add_key(self, request_id, key, expire_time, local_cnt, in_redis, in_disk, in_couchDB, datasize=0):
        datainfo = DataInfo(request_id, key, time.time() + expire_time, local_cnt, in_redis, in_disk, in_couchDB, datasize)
        self.requests_keys_info[request_id][key] = datainfo

        # Never expire: when data not in redis!
        if in_redis:
            self.expire_queue.put(datainfo)


flow_monitor = FlowMonitor()
