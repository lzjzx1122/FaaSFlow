FUNCTION_INFO_ADDRS = {'genome': '../../benchmark/generator/genome', 'epigenomics': '../../benchmark/generator/epigenomics',
                                                'soykb': '../../benchmark/generator/soykb', 'cycles': '../../benchmark/generator/cycles',
                                                'fileprocessing': '../../benchmark/fileprocessing', 'wordcount': '../../benchmark/wordcount',
                                                'illgal_recognizer': '../../benchmark/illgal_recognizer', 'video': '../../benchmark/video'}
DATA_MODE = 'optimized' # raw, optimized
CONTROL_MODE = 'WorkerSP' # WorkerSP, MasterSP
MASTER_HOST = '172.20.185.158:8000'
COUCHDB_URL = 'http://openwhisk:openwhisk@172.20.185.158:5984/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
CLEAR_DB_AND_MEM = True