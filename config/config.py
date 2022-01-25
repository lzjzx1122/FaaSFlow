COUCHDB_URL = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
REDIS_HOST = '10.2.64.8'
REDIS_PORT = 6380
REDIS_DB = 0
GATEWAY_ADDR = '10.2.64.8:7000'
MASTER_HOST = '10.2.64.8:8000'
WORKFLOW_YAML_ADDR = {'fileprocessing': '/home/openwhisk/Workflow/benchmark/fileprocessing/flat_workflow.yaml',
                  'illgal_recognizer': '/home/openwhisk/Workflow/benchmark/illgal_recognizer/flat_workflow.yaml',
                  'video': '/home/openwhisk/Workflow/benchmark/video/flat_workflow.yaml',
                  'wordcount': '/home/openwhisk/Workflow/benchmark/wordcount/flat_workflow.yaml',
                  'cycles': '/home/openwhisk/Workflow/benchmark/generator/cycles/flat_workflow.yaml',
                  'epigenomics': '/home/openwhisk/Workflow/benchmark/generator/epigenomics/flat_workflow.yaml',
                  'genome': '/home/openwhisk/Workflow/benchmark/generator/genome/flat_workflow.yaml',
                  'soykb': '/home/openwhisk/Workflow/benchmark/generator/soykb/flat_workflow.yaml'}
NETWORK_BANDWIDTH = 25 * 1024 * 1024 / 4 # 25MB/s / 4
NET_MEM_BANDWIDTH_RATIO = 15 # mem_time = net_time / 15
CONTAINER_MEM = 256 * 1024 * 1024 # 256MB
NODE_MEM = 256 * 1024 * 1024 * 1024 # 256G
RESERVED_MEM_PERCENTAGE = 0.2
GROUP_LIMIT = 100
RPMs = {'genome-25': [2, 4, 6, 8], 'genome-50': [2, 4, 6, 8, 10], 'genome-75': [2, 4, 6, 8, 10], 'genome-100': [2, 4, 6, 8, 10],
'video-25': [4, 8, 16, 24], 'video-50': [8, 16, 24, 32, 40], 'video-75': [8, 16, 24, 32, 40], 'video-100': [8, 16, 24, 32, 40]}
FUNCTION_INFO_ADDRS = {'genome': '../../benchmark/generator/genome', 'epigenomics': '../../benchmark/generator/epigenomics',
                                                'soykb': '../../benchmark/generator/soykb', 'cycles': '../../benchmark/generator/cycles',
                                                'fileprocessing': '../../benchmark/fileprocessing', 'wordcount': '../../benchmark/wordcount',
                                                'illgal_recognizer': '../../benchmark/illgal_recognizer', 'video': '../../benchmark/video'}
DATA_MODE = 'raw' # raw, optimized
CONTROL_MODE = 'WorkerSP' # WorkerSP, MasterSP
CLEAR_DB_AND_MEM = True
