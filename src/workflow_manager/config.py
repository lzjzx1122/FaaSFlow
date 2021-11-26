FUNCTION_INFO_ADDRS = {'genome': '~/FaaSFlow/benchmark/generator/genome', 'epigenomics': '~/FaaSFlow/benchmark/generator/epigenomics',
                                                'soykb': '~/FaaSFlow/benchmark/generator/soykb', 'cycles': '~/FaaSFlow/benchmark/generator/cycles',
                                                'fileprocessing': '~/FaaSFlow/benchmark/fileprocessing', 'wordcount': '~/FaaSFlow/benchmark/wordcount',
                                                'illgal_recognizer': '~/FaaSFlow/benchmark/illgal_recognizer', 'video': '~/FaaSFlow/benchmark/video'}
DATA_MODE = 'raw' # raw, optimized
CONTROL_MODE = 'WorkerSP' # WorkerSP, MasterSP
MASTER_HOST = '172.20.185.158:8000'
COUCHDB_URL = 'http://openwhisk:openwhisk@172.20.185.158:5984/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
CLEAR_DB_AND_MEM = True