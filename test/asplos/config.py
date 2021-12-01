GATEWAY_ADDR = '172.20.185.158:7000'
COUCHDB_URL = 'http://openwhisk:openwhisk@172.20.185.158:5984/'
WORKFLOW_YAML_ADDR = {'fileprocessing': '../../../benchmark/fileprocessing/flat_workflow.yaml',
                  'illgal_recognizer': '../../../benchmark/illgal_recognizer/flat_workflow.yaml',
                  'video': '../../../benchmark/video/flat_workflow.yaml',
                  'wordcount': '../../../benchmark/wordcount/flat_workflow.yaml',
                  'cycles': '../../../benchmark/generator/cycles/flat_workflow.yaml',
                  'epigenomics': '../../../benchmark/generator/epigenomics/flat_workflow.yaml',
                  'genome': '../../../benchmark/generator/genome/flat_workflow.yaml',
                  'soykb': '../../../benchmark/generator/soykb/flat_workflow.yaml'}
NETWORK_BANDWIDTH = 25 * 1024 * 1024 / 4 # 25MB/s / 4
RPMs = {'gen-25': [6, 8, 10, 20], 'gen-50': [6, 8, 10, 20], 'gen-75': [6, 8, 10, 20, 30], 'gen-100': [6, 8, 10, 20, 30, 40],
'vid-25': [4, 6, 8, 10], 'vid-50': [4, 6, 8, 10, 15], 'vid-75': [4, 6, 8, 10, 15, 20], 'vid-100': [4, 6, 8, 10, 15, 20]}
