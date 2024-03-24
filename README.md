# FaaSFlow
[![GitHub release (with filter)](https://img.shields.io/github/v/release/lzjzx1122/faasflow?label=Release%20Version)](https://github.com/lzjzx1122/FaaSFlow/releases/tag/v2.0)
[![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/lzjzx1122/faasflow?label=Last%20Commit)](https://github.com/lzjzx1122/FaaSFlow/commits/main)
[![Static Badge](https://img.shields.io/badge/Organization_Website-EPCC-purple)](http://epcc.sjtu.edu.cn)


### New Features 
```
- Sep 5, 2023 (FaaSFlow v2.0) - DataFlower is a built-in workflow orchestration scheme!
- Dec 2, 2021 (FaaSFlow v1.0) - FaaFlow public version release.
```

### Ongoing Features
```
- Checkpoint/Restore for serverless workflows.
```

## Introduction

FaaSFlow is a serverless workflow framework designed to enhance workflow execution efficiency. It achieves this through the adoption of a worker-side workflow scheduling pattern, thereby reducing scheduling overhead. Additionally, it employs an adaptive storage library that leverages local memory for data transfer between functions situated on the same node.

In FaaSFlow, there is a built-in execution scheme called DataFlower, which implements the data-flow paradigm for serverless workflow orchestration. With the DataFlower scheme, a container is abstracted to be several function logic units and a data logic unit. The function logic unit executes the functions, while the data logic unit manages data transmission asynchronously. Furthermore, FaaSFlow with DataFlower will employ a collaborative communication mechanism between hosts and containers to facilitate efficient data transfer in conjunction with the adaptive storage library.

The FaaSFlow paper in *ASPLOS'22* is [FaaSFlow: enable efficient workflow execution for function-as-a-service](https://dl.acm.org/doi/10.1145/3503222.3507717).

The DataFlower paper in *ASPLOS'24* is [DataFlower: Exploiting the Data-flow Paradigm for Serverless Workflows](https://arxiv.org/abs/2304.14629).

[![Security Status](https://s.murphysec.com/badge/lzjzx1122/FaaSFlow.svg)](https://www.murphysec.com/p/lzjzx1122/FaaSFlow)


## Hardware Dependencies and Private IP Address

1. Our experiment setup requires at least three nodes (one gateway node, one storage node, and one or more worker nodes). For the gateway node and the storage node, the minimal hardware requirements is \{Cores: 8, DRAM: 16GB, Disk: 200GB SSD\}. For each worker node, the minimal hardware requirements is \{Cores: 16, DRAM: 64GB, Disk: 200GB SSD\}. All nodes run Ubuntu 20.04. The remote storage node is installed with Kafka to transfer intermediate data and CouchDB to collect logs. The gateway node is also responsible for generating workflow invocations.


2. Please save the private IP address of the gateway node as the **<gateway_ip>**, the private IP address of the remote storage node as the **<storage_ip>**, and the private IP address of each worker node as the **<worker_ip>**. 



## About Config Setting

There are 3 places for config settings. `src/container/container_config.py` specifies CouchDB and Kafka's address. You need to fill in the correct IP so that the application code can directly connect to the database inside the container environment. Besides, `scripts/kafka/docker-compose.yml` specifies the Kafka's configuration. All other configurations are in `config/config.py`.

Currently DataFlower support the worker nodes number less or equal than three, while the elements number of `WORKER_ADDRS` in `config/config.py` represents whether the evaluation will be done within a single worker node or among multiple worker nodes. To run DataFlower under more than three worker nodes, the ip route table of each function of each benchmark should be assigned in `*_sp_ip_idx` in `src/workflow_manager/gateway.py`. 

## Installation and Software Dependencies

Clone our code `https://github.com/lzjzx1122/FaaSFlow.git` and:


1. Reset `WORKER_ADDRS` configuration with your <worker_ip> in `config/config.py`. It will specify your workers' addresses.
   
   Reset `GATEWAY_IP` as `<gateway_ip>` in `config/config.py`.

2. Reset `COUCHDB_IP` as `<storage_ip>` in `config/config.py`, and `COUCHDB_URL` as `http://openwhisk:openwhisk@<storage_ip>:5984/`  in `src/container/container_config.py`. These parameters will specify the corresponding CouchDB for metric logging.

   Reset `KAFKA_IP` as `<storage_ip>` in `config/config.py`, `KAFKA_URL` as `<storage_ip>:9092/` in `src/container/container_config.py`, and `KAFKA_ADVERTISED_LISTENERS` as `PLAINTEXT://<storage_ip>:9092,PLAINTEXT_INTERNAL://broker:29092` in `scripts/kafka/docker-compose.yml`

3. Then, clone the modified code into each node.

4. Run `scripts/db_setup.bash` on the remote storage node and `scripts/gateway_setup.bash` on the gateway node. These scripts install docker, Kafka, CouchDB, some python packages. 

5. On each worker node: Run `scripts/worker_setup.bash`. This installs docker, Redis, and some python packages, and builds docker images from 4 benchmarks.

## Worker Start-up

The following operations are the prerequisites to run the test scripts.

Firstly, enter `src/workflow_manager`. 

Then, start the gateway on the gateway node by the following command: 
```
    python3 gateway.py <gateway_ip> 7000           (gateway start)
```

Finally, start the engine proxy with the local <worker_ip> on each worker node by the following <span id="jump">command</span>: 
```
    python3 test_server.py <worker_ip>             (proxy are ready to serve)
```

Now you have finished all the operations and are allowed to send invocations by `*test.py` scripts under `test/`. Detailed script usage is introduced in [Run Experiment](#jumpexper).
    
**Note:** We recommend restarting the `test_server.py` on each worker node and the `gateway.py` on the gateway node whenever you start the `*test.py` script, to avoid any potential bug.

## <span id="jumpexper">Run Experiment</span>

We provide some test scripts under `test/`. And the expected results is in `test/expected_results`.
**<span id="note">Note:**</span> We recommend restarting all `test_server.py` and `gateway.py` processes whenever you start the `*test.py` script, to avoid any potential bug. The restart will clear all background function containers and reclaim the memory space. 

### Response Latency

Directly run on the gateway node: 
```
    python3 async_test.py
```

### Peak Throughput

Directly run on the gateway node: 
```
    python3 sync_test.py
```

### Colocating Multiple Workflows

Directly run on the gateway node: 
```
    python3 async_colocation_test.py
```

## Cite
Welcome to cite FaaSFlow in ASPLOS'22 by:
```
@inproceedings{10.1145/3503222.3507717,
   author = {Li, Zijun and Liu, Yushi and Guo, Linsong and Chen, Quan and Cheng, Jiagan and Zheng, Wenli and Guo, Minyi},
   title = {FaaSFlow: Enable Efficient Workflow Execution for Function-as-a-Service},
   year = {2022},
   address = {New York, NY, USA},
   doi = {10.1145/3503222.3507717},
   booktitle = {Proceedings of the 27th ACM International Conference on Architectural Support for Programming Languages and Operating Systems},
   pages = {782–796},
   numpages = {15},
   location = {Lausanne, Switzerland},
   series = {ASPLOS '22}
}
```

and DataFlower in ASPLOS'24 by:
```
@inproceedings{10.1145/3623278.3624755,
   author = {Li, Zijun and Xu, Chuhao and Chen, Quan and Zhao, Jieru and Chen, Chen and Guo, Minyi},
   title = {DataFlower: Exploiting the Data-flow Paradigm for Serverless Workflow Orchestration},
   year = {2024},
   address = {New York, NY, USA},
   doi = {10.1145/3623278.3624755},
   booktitle = {Proceedings of the 28th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 4},
   pages = {57–72},
   numpages = {16},
   location = {Vancouver, BC, Canada},
   series = {ASPLOS '23}
}
```
