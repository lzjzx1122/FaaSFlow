NETWORK_BANDWIDTH = 25 * 1024 * 1024 / 4 # 25MB/s / 4
NET_MEM_BANDWIDTH_RATIO = 15 # mem_time = net_time / 15
CONTAINER_MEM = 256 * 1024 * 1024 # 256MB
NODE_MEM = 256 * 1024 * 1024 * 1024 # 256G
RESERVED_MEM_PERCENTAGE = 0.2
WORKFLOW_YAML_ADDR = {'fileprocessing': '../benchmark/fileprocessing/flat_workflow.yaml',
                  'illgal_recognizer': '../benchmark/illgal_recognizer/flat_workflow.yaml',
                  'video': '../benchmark/video/flat_workflow.yaml',
                  'wordcount': '../benchmark/wordcount/flat_workflow.yaml',
                  'cycles': '../benchmark/generator/cycles/flat_workflow.yaml',
                  'epigenomics': '../benchmark/generator/epigenomics/flat_workflow.yaml',
                  'genome': '../benchmark/generator/genome/flat_workflow.yaml',
                  'soykb': '../benchmark/generator/soykb/flat_workflow.yaml'}
COUCHDB_URL = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0