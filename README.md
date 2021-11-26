# FaaSFlow

## Introduction

FaaSFlow is a serverless workflow engine that enables efficient workflow execution in 2 ways: a worker-side workflow schedule pattern to reduce scheduling overhead, and a adaptive storage library to use local memory to transfer data between functions on the same node.

## Installation and Software Dependencies

1. In our experiment setup, we use aliyun ecs instance installed with Ubuntu 18.04 (ecs.c6e.2xlarge, cores: 8, DRAM: 16GB) for each worker node, and a ecs.g6e.4xlarge(cores: 16, DRAM: 64GB) instance for database node installed with Ubuntu 18.04 and CouchDB.

On database node:

2. Create following database on CouchDB: workflow_latency, results, log

3. Reset src/grouping/node_info.yaml, this includes your worker url and worker scale_limit. Run scripts/grouping.bash to build grouping result for each benchmark.

On each worker node:

4. Install Docker: https://docs.docker.com/engine/install/ubuntu/, install redis, and install python packages: gevent, redis, couchdb, docker, flask, psutil.

5. Reset configuration files base on your experiment environment: src/container/config.py, src/grouping/config.py, src/workflow_manager/config.py. Configuration includes your CouchDB and redis address, data_mode(with or without adaptive storage and data caching), control_mode(MasterSP or WorkerSP),...

6. Run scripts/worker_setup.bash to build docker images for benchmarks.

## Start-up

1. Enter src/workflow_manager, start a proxy for each worker node: 
- python3 proxy.py \<worker_ip\> \<worker_port\> 

2. For MasterSP, start another proxy at any node as master node. Set MASTER_HOST src/workflow_manager/config.py as corresponding address.

3. Start a gateway also at any node you like. The gateway opens an api for benchmark quick-startup. Choose workflow(fileprocessing, wordcount, video, illgal_recognizer, cycles, epigenomics, genome, soykb) and request_id. You can view the results in 'results' database in CouchDB. 
- python3 gateway.py \<gateway_ip\> \<gateway_port\> 
- POST /run {"workflow": "...", "request_id": "1"}

## Run Experiment

Some experiment scripts are provided in test/asplos, and experiment data can be found under test/asplos/data. Start one gateway.py and several proxy.py before conducting your experiment. Reset configurations(CONTROL_MODE: MasterSP or WorkerSP, DATA_MODE: raw or optimized) to see differences.

1. Schedule Overhead: run scheduling_overhead.py

2. End-to-End Latency: run e2e_latency.py

3. Data Overhead: run data_overhead.py