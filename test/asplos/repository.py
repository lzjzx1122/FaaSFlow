from typing import Any, List
import couchdb
import redis
import json
import config

class Repository:
    def __init__(self):
        self.redis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        self.couch = couchdb.Server(config.COUCHDB_URL)

    def clear_couchdb_results(self):
        self.couch.delete('results')
        self.couch.create('results')
    
    def clear_redis_cache(self):
        self.redis.flushall()

    def clear_couchdb_workflow_latency(self):
        self.couch.delete('workflow_latency')
        self.couch.create('workflow_latency')

    def get_critical_path_functions(self, workflow):
        db_name = workflow + '_workflow_metadata'
        result = []
        for _id in self.couch[db_name]:
            if 'critical_path_functions' in self.couch[db_name][_id]:
                result = self.couch[db_name][_id]['critical_path_functions']
        return result
    
    def get_latencies(self):
        return self.couch['workflow_latency']