import gevent

from config import config
import couchdb

couchdb_url = config.COUCHDB_URL


class Repository:
    def __init__(self):
        self.couchdb = couchdb.Server(couchdb_url)
        self.waiting_logs = []

    def create_request_doc(self, request_id: str):
        if request_id in self.couchdb['results']:
            # self.couchdb['results'].delete(self.couchdb['results'][request_id])
            self.couchdb['results'].purge([self.couchdb['results'][request_id]])
        self.couchdb['results'][request_id] = {}

    def clear_couchdb_workflow_latency(self):
        self.couchdb.delete('workflow_latency')
        self.couchdb.create('workflow_latency')

    def clear_couchdb_results(self):
        self.couchdb.delete('results')
        self.couchdb.create('results')

    def save_scalability_config(self, dir_path):
        self.couchdb['results']['scalability_config'] = {'dir': dir_path}

    def save_kafka_config(self, KAFKA_CHUNK_SIZE):
        self.couchdb['results']['kafka_config'] = {'KAFKA_CHUNK_SIZE': KAFKA_CHUNK_SIZE}

    def get_kafka_config(self):
        try:
            return self.couchdb['results']['kafka_config']
        except Exception:
            return None

    def save_latency(self, log):
        self.couchdb['workflow_latency'].save(log)

    def save_redis_log(self, request_id, size, time):
        self.waiting_logs.append({'phase': 'redis', 'request_id': request_id, 'size': size, 'time': time})
        # self.couchdb['workflow_latency'].save({'phase': 'redis', 'request_id': request_id, 'size': size, 'time': time})

    def get_latencies(self, phase):
        requests_logs = {}
        for k in self.couchdb['workflow_latency']:
            doc = self.couchdb['workflow_latency'][k]
            if doc['phase'] == phase:
                request_id = doc['request_id']
                if request_id not in requests_logs:
                    requests_logs[request_id] = []
                requests_logs[request_id].append(doc)
        return requests_logs

    def upload_waiting_logs(self):
        tmp_db = self.couchdb['workflow_latency']
        for log in self.waiting_logs:
            tmp_db.save(log)
