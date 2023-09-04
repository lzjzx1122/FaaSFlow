# DataFlower

## Introduction

DataFlower is a scheme that achieves the data-flow paradigm for the serverless workflows. In DataFlower, a container is abstracted to be a function logic unit and a data logic unit. The function logic unit runs the functions, and the data logic unit handles the data transmission asynchronously. Moreover, a host-container collaborative communication mechanism is used to support the efficient data transfer.

[//]: # (FaaSFlow is a serverless workflow engine that enables efficient workflow execution in 2 ways: a worker-side workflow schedule pattern to reduce scheduling overhead, and an adaptive storage library to use local memory to transfer data between functions on the same node.)

*Our work has been accepted by ASPLOS' 24. The paper is [DataFlower: Exploiting the Data-flow Paradigm for Serverless Workflows](https://arxiv.org/abs/2304.14629)*

[![Security Status](https://s.murphysec.com/badge/lzjzx1122/FaaSFlow.svg)](https://www.murphysec.com/p/lzjzx1122/FaaSFlow)


## Hardware Depedencies and Private IP Address

1. In our experiment setup, we use three aliyun ecs instances ecs.g7.4xlarge (cores: 16, DRAM: 64GB) for the worker nodes, and two ecs.c7.2xlarge (cores: 8, DRAM: 16GB) instances for the remote storage node and the gateway node. All nodes run Ubuntu 20.04. The remote storage node is installed with Kafka to transfer intermediate data and CouchDB to collect log. The gateway node is also responsible for generating workflow invocations.


2. Please save the private IP address of the gateway node as the **<gateway_ip>**, the private IP address of the remote storage node as the **<storage_ip>**, and the private IP address of the other 3 worker nodes as the **<worker_ip>**. 

## About Config Setting

There are 3 places for config setting. `src/container/container_config.py` specifies CouchDB and Kafka's address, you need to fill in correct ip so that application code can directly connect to database inside container environment. Besides, `scripts/kafka/docker-compose.yml` speficies the Kafka's configuration. All other configurations are in `config/config.py`.

## Installation and Software Dependencies

Clone our code `https://github.com/lzjzx1122/FaaSFlow.git` and:


1. Reset `WORKER_ADDRS` configuration with your <worker_ip> in `config/config.py`. It will specify your workers' addresses.
   
   Reset `GATEWAY_IP` as `<gateway_ip>` in `config/config.py`.

2. Reset `COUCHDB_IP` as `<storage_ip>` in `config/config.py`, and `COUCHDB_URL` as `http://openwhisk:openwhisk@<storage_ip>:5984/`  in `src/container/container_config.py`. These parameters will specify the corresponding CouchDB for metric logging.

   Reset `KAFKA_IP` as `<storage_ip>` in `config/config.py`, `KAFKA_URL` as `<storage_ip>:9092/` in `src/container/container_config.py`, and `KAFKA_ADVERTISED_LISTENERS` as `PLAINTEXT://<storage_ip>:9092,PLAINTEXT_INTERNAL://broker:29092` in `scripts/kafka/docker-compose.yml`

3. Then, clone the modified code into each node (5 nodes total).

4. Run `scripts/db_setup.bash` on the remote storage node and `scripts/gateway_setup.bash` on the gateway node. These scripts install docker, Kafka, CouchDB, some python packages. 

5. On each worker node: Run `scripts/worker_setup.bash`. This install docker, Redis, some python packages, and build docker images from 4 benchmarks.

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

Now you have finished all the operations and are allowed to send invocations by `*test.py` scripts under `test/`. Detailed scripts usage is introduced in [Run Experiment](#jumpexper).
    
**Note:** We recommend restarting the `test_server.py` on each worker node and the `gateway.py` on the gateway node whenever you start the `*test.py` script, to avoid any potential bug.

## <span id="jumpexper">Run Experiment</span>

We provide some test scripts under `test/`.
**<span id="note">Note:**</span> We recommend to restart all `test_server.py` and `gateway.py` processes whenever you start the `*test.py` script, to avoid any potential bug. The restart will clear all background function containers and reclaim the memory space. 

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
Welcome to cite DataFlower by:
```
@misc{li2023dataflower,
      title={DataFlower: Exploiting the Data-flow Paradigm for Serverless Workflow Orchestration}, 
      author={Zijun Li and Chuhao Xu and Quan Chen and Jieru Zhao and Chen Chen and Minyi Guo},
      year={2023},
      eprint={2304.14629},
      archivePrefix={arXiv},
      primaryClass={cs.DC}
}
```
