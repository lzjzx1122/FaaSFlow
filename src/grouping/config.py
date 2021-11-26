NETWORK_BANDWIDTH = 25 * 1024 * 1024 / 4 # 25MB/s / 4
NET_MEM_BANDWIDTH_RATIO = 15 # mem_time = net_time / 15
CONTAINER_MEM = 256 * 1024 * 1024 # 256MB
NODE_MEM = 256 * 1024 * 1024 * 1024 # 256G
RESERVED_MEM_PERCENTAGE = 0.2
WORKFLOW_YAML_ADDR = {'fileprocessing': '~/FaaSFlow/benchmark/fileprocessing/flat_workflow.yaml',
                  'illgal_recognizer': '~/FaaSFlow/benchmark/illgal_recognizer/flat_workflow.yaml',
                  'video': '~/FaaSFlow/benchmark/video/flat_workflow.yaml',
                  'wordcount': '~/FaaSFlow/benchmark/wordcount/flat_workflow.yaml',
                  'cycles': '~/FaaSFlow/benchmark/generator/cycles/flat_workflow.yaml',
                  'epigenomics': '~/FaaSFlow/benchmark/generator/epigenomics/flat_workflow.yaml',
                  'genome': '~/FaaSFlow/benchmark/generator/genome/flat_workflow.yaml',
                  'soykb': '~/FaaSFlow/benchmark/generator/soykb/flat_workflow.yaml'}
COUCHDB_URL = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0