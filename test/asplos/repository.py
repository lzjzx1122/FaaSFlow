import couchdb
import sys
sys.path.append('../../config')
import config

class Repository:
    def __init__(self):
        self.couch = couchdb.Server(config.COUCHDB_URL)

    def clear_couchdb_results(self):
        self.couch.delete('results')
        self.couch.create('results')

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
    
    def get_latencies(self, request_id, phase):
        docs = []
        for _id in self.couch['workflow_latency']:
            doc = self.couch['workflow_latency'][_id]
            if doc['request_id'] == request_id and doc['phase'] == phase:
                docs.append(doc)
        return docs