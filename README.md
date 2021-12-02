# FaaSFlow

## Introduction

FaaSFlow is a serverless workflow engine that enables efficient workflow execution in 2 ways: a worker-side workflow schedule pattern to reduce scheduling overhead, and a adaptive storage library to use local memory to transfer data between functions on the same node.

## Installation and Software Dependencies

1. In our experiment setup, we use aliyun ecs instance installed with Ubuntu 18.04 (ecs.g7.2xlarge, cores: 8, DRAM: 32GB) for each worker node, and a ecs.g6e.4xlarge(cores: 16, DRAM: 64GB) instance for database node installed with Ubuntu 18.04 and CouchDB. Please save the private IP addredd of the storage node as the <master_ip>, and save the private IP addredd of other 7 worker nodes as the <worker_ip>.

2. Clone our code `https://github.com/lzjzx1122/FaaSFlow.git` into each nodes (8 nodes total).

On database node:

3. Reset `worker_address` configuration with the `worker_ip` on `src/grouping/node_info.yaml`. it will specify your <worker_ip> and <worker_port>.

4. Run: `scripts/db_setup.bash`. This install docker, couchdb, some python packages, and build grouping results from 8 benchmarks.

On each worker node:

5. Reset `COUCHDB_URL`  in `src/container/config.py`, `src/workflow_manager/config.py`, `test/asplos/config.py` to the corresponding db you build previously.

6. Run `scripts/worker_setup.bash`. This install docker, redis, some python packages, and build docker images from 8 benchmarks.

## Start-up

1. Enter `src/workflow_manager`, `config.py` includes serveral config that you should pay attention to: `DATA_MODE=raw/optimized`, `CONTROL_MODE=MasterSP/WorkerSP`. If faasflow-faastore is to be evaluated, the configurations should be `DATA_MODE=optimized`, `CONTROL_MODE=WorkerSP`. If hyperflow is to be evaluated, the configurations should be `DATA_MODE=raw`, `CONTROL_MODE=MaterSP`. 

2. Firstly, start a proxy on each worker node: `python3 proxy.py <worker_ip> <worker_port>`. Then start a gateway at the storage node: `python3 gateway.py <master_ip> <gateway_port>`, they are defined by <GATEWAY_ADDR> = <master_ip>:<gateway_port> in `test/asplos/config.py`.

3. If you would like to run scripts under WorkerSP, you have finished all the operations and can send invocations for performance test.

4. If you would like to run scripts under MasterSP, start another proxy at the storage node as master node: `python3 proxy.py <master_ip> <master_port>`, and they are defined by <MASTER_HOST> = <master_ip>:<master_port> in `src/workflow_manager/config.py`.

## Run Experiment

We provide some test scripts under `test/asplos`.
We recommend to restart the `proxy.py` on each worker node and the `gateway.py` on the master node whenever you start the `run.py` script, to avoid any potential bugs.

### Component Overhead: overhead of one workflow engine

1. Start a proxy at any worker node and record its pid.

2. Run: `python3 run.py --pid=<pid>`

### Data Overhead: total time spend on data transmission

1. On each node, reset DATA_MODE in `src/workflow_manager/config.py` to `raw`(faastore unabled) or `optimized`(faastore enabled), and start a proxy. Start a gateway on storage node also.

2. Run: `python3 run.py --datamode=<DATA_MODE>`

### End-to-End Latency: run one-by-one and run all-at-once

1. On each node, reset DATA_MODE in `src/workflow_manager/config.py` to `raw`(faastore unabled) or `optimized`(faastore enabled), and start a proxy. Start a gateway on storage node also.

2. Run: `python3 run.py --datamode=<DATA_MODE> --mode=<MODE>` DATA_MODE = `raw` or `optimized`, MODE = `single` or `corun`

### Scheduler Scalability: the overhead of graph scheduler when scale-up total nodes of one workflow

1. Run: `python3 run.py`

### Schedule Overhead: time spend on scheduling tasks

1. On each node, reset CONTROL_MODE in `src/workflow_manager/config.py` to `MasterSP` or `WorkerSP`, then start proxy and gateway as we mentioned in previous section.

2. Run: `python3 run.py --controlmode=<CONTROL_MODE>` CONTROL_MODE = `MasterSP` or `WorkerSP`

### 99%-ile latency at 50MB/s, 6 request/min for all benchmark

1. Download wondershaper at `https://github.com/magnific0/wondershaper` to limit bandwidth.

2. At database node set bandwidth to 50MB/s:  `cd <your_wondershaper_path>/wondershaper`, and then run `./wondershaper -a docker0 -c` to clear the previous bandwidth setting. Then you can run `./wondershaper -a docker0 -u 409600 -d 409600` to set the network bandwidth to 50MB/s. Remember start a gateway ` python3 gateway.py <gateway_ip> <gateway_port> ` on this node also.

3. On each node, reset DATA_MODE in `src/workflow_manager/config.py` to raw(faastore unabled) or optimized(faastore enabled), and start a proxy. 

4. Run `python3 run.py --datamode=<DATA_MODE>`

### 99%-ile latency at from 25MB/s-100MB/s, and with dfferent request/min for benchmark genome and video

1. `cd <your_wondershaper_path>/wondershaper`, and then run `./wondershaper -a docker0 -c` to clear the previous bandwidth setting.

2. Run `./wondershaper -a docker0 -u 204800 -d 204800` to set a 25MB/s bandwidth limit (`-u 409600 -d 409600` corresponds to 50MB/s, `-u 614400 -d 614400` corresponds to 75MB/s, `-u 819200 -d 819200` corresponds to 100MB/s).

3. Then run the script. For example, `python3 tail_latency.py --bandwidth=25 --datamode=raw --workflow=genome` represents Gen-25MB/s(hyperflow-serverless), `python3 tail_latency.py --bandwidth=75 --datamode=optimized --workflow=video` represents Vid-75MB/s(faasflow-faastore). When datamode is changed to `optimmized`, remember to save it to the `DATA_MODE` of `config.py` in each worker node and the master gateway.

4. If you find that all execution logs are marked as `timeout`, please restart the `proxy.py` on each worker node and the `gateway.py` on the master node whenever you start the `run.py` script, to avoid any potential bugs.
