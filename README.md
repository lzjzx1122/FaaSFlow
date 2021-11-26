# FaaSFlow

## Introduction

FaaSFlow is a serverless workflow engine that enables efficient workflow execution in 2 ways: a worker-side workflow schedule pattern to reduce scheduling overhead, and a adaptive storage library to use local memory to transfer data between functions on the same node.

## Installation and Software Dependencies

1. In our experiment setup, we use aliyun ecs instance installed with Ubuntu 18.04 (ecs.c6e.2xlarge, cores: 8, DRAM: 16GB) for each worker node, and a ecs.g6e.4xlarge(cores: 16, DRAM: 64GB) instance for database node installed with Ubuntu 18.04 and CouchDB.

2. Clone our code: `https://github.com/lzjzx1122/FaaSFlow.git`

On database node:

3. Reset configuration on `src/grouping/node_info.yaml`. This specify your worker address and scale_limit.

4. Run: `scripts/db_setup.bash`. This install docker, couchdb, some python packages, and build grouping results from 8 benchmarks.

On each worker node:

5. Reset COUCHDB_URL in `src/container/config.py`, `src/workflow_manager/config.py`, `test/asplos/config.py` to the corresponding db you build previously.

6. Run `scripts/worker_setup.bash`. This install docker, redis, some python packages, and build docker images from 8 benchmarks.

## Start-up

1. Enter `src/workflow_manager`. `config.py` includes serveral config that you should pay attention to: `DATA_MODE=raw/optimized`, `CONTROL_MODE=MasterSP/WorkerSP`. If you run under MasterSP, MASTER_HOST is where you start your master node.

2. Start a proxy on each worker node: `python3 proxy.py <worker_ip> <worker_port> `

3. For MasterSP, start another proxy at any node as master node, using corresponding ip and port in MASTER_HOST.

4. Start a gateway also at any node you like. The gateway opens an api for benchmark quick-startup. Choose workflow(fileprocessing, wordcount, video, illgal_recognizer, cycles, epigenomics, genome, soykb) and request_id. You can view the results in 'results' database in CouchDB. 

- ` python3 gateway.py <gateway_ip> <gateway_port> `
- ` POST /run {"workflow": "...", "request_id": "1"} `

## Run Experiment
