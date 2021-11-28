NETWORK_BANDWIDTH = 25 * 1024 * 1024 / 4 # 25MB/s / 4
NET_MEM_BANDWIDTH_RATIO = 15 # mem_time = net_time / 15
CONTAINER_MEM = 256 * 1024 * 1024 # 256MB
NODE_MEM = 256 * 1024 * 1024 * 1024 # 256G
RESERVED_MEM_PERCENTAGE = 0.2
WORKFLOW_YAML_ADDR = {10: 'wdl/10.yaml', 25: 'wdl/25.yaml', 50: 'wdl/50.yaml', 100: 'wdl/100.yaml', 200: 'wdl/200.yaml'}
COUCHDB_URL = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0