# ActionManager

The only provided API is `ActionManager`, and `example.py` shows how to use the API:

```
from function_manager import FunctionManager
manager = FunctionManager("functions")
for _ in range(10):
    request_id = uuid.uuid4().hex
    manager.run("utility", request_id, {"runtime": 1, "output_size":10})
```
Firstly, you need to create an `ActionManager` instance. For example, the created instance in the above code is `manager`. In this way, if you want to execute a function, you can call `manager.run(function_name, request_id, parameters)` directly.

To execute functions successfully, another thing you need to do is to create a directory which contains a config file and all functions that you want to execute. For instance, you can see a directory `functions`. In this directory, you can see a config file `function_info.yaml` and a subdirectory `utility`. The subdirectory `utility` contains a python file, where a function named `main(para)` is defined. The following shows the formation of the config file `function_info.yaml`.

## Config file

The config file defines all functions workable on this machine. it should be a yaml file like the following:
```yaml
functions:
  - name: utility
    qos_time: 100
    qos_requirement: 0.99
    max_containers : 10
    packages:
      - numpy
      - scipy
```

the meaning of each field:
- `functions`: a list containing all functions.
  - `name`: the name of function.
  - `qos_time`: the maximum execution time of QOS requirement.
  - `qos_requirement`: the precentage that should meet the QOS requirment.
  - `max_containers`: the maximum number of containers that the function can create for itself.
  - `packages`: a list containing all packages that the function need.
  
Now you can execute `example.py`. When execution completes, you can execute `curl -X GET http://admin:password@127.0.0.1:5984/results` in a terminal to list all documents of database. A document means result of an execution. 

## Note
When executing `example.py`, if you see an error `port is already allocated`, this means that there exists a running container occupying the port. To solve this problem, you can execute the command `docker ps` in a terminal to list all running containers. Next you can stop and remove a running container by executing `docker stop #id` and `docker rm #id`. Please not to remove two containers: `ubuntu16.04` and `couchdb`.
