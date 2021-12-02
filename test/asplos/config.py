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
RPMs = {'genome-25': [2, 4, 6, 8], 'genome-50': [2, 4, 6, 8, 10], 'genome-75': [2, 4, 6, 8, 10], 'genome-100': [2, 4, 6, 8, 10],
'video-25': [4, 8, 16, 24], 'video-50': [8, 16, 24, 32, 40], 'video-75': [8, 16, 24, 32, 40], 'video-100': [8, 16, 24, 32, 40]}
