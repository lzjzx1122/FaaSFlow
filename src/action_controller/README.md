# Action Controller

## config file
the config file defines every action workable on this machine. it should be a yaml file like the following:
```yaml
max_container: 10
actions:
  - name: test_action1
    pwd: test1
    image: test_img1
    qos_time: 100
    qos_requirement: 0.99
  - name: test_action2
    pwd: test2
    image: test_img2
    qos_time: 200
    qos_requirement: 0.95
```

the meaning of each field:
- `max_container`: the maximum number of containers an action can create for itself.
- `actions`: a list containing the information of actions:
  - `name`: the name of action.
  - `pwd`: the passphrase for decrypting action's zipfile.
  - `image`: the name of the docker image for this action.
  - `qos_time`: the maximum execution time of QOS requirement.
  - `qos_requirement`: the precentage that shoud meet the QOS requirment.

## restful API
proxy server runs at port 5000. it receives the following requests:
- `/run/<action_name>`: POST request. return a json. send a user request to run the action.
- `/status`: GET request. return a json. get the status of controller.
- `/end`: 

### run/<action_name>
send the request to a container to actually run the code once. the target action is `action_name`.

it requires a json object:
```json
{
    "request_id": "akeyforcouchdb",
    "data": {
        "something": "send to container"
    }
}
```

the meaning of each field:
- `request_id`: it should be a unique key. it's used as the key to store result in couchdb
- `data`: the actual input to send to container

it will store the result and running info in `action_results` database in couchdb.
```json
{
    "result": {
        "result": "return by container"
    },
    "duration": 0.05,
    "start": 12334.0,
    "end": 12334.5
}
```

the meaning of each field:
- `result`: the actual result return by container
- `duration`: the run time taken in container
- `start`: the time when container receives request (may not be the time when controller receives request)
- `end`: the time when contaienr finish request

it returns `200 OK` if success

### status
get the current status of controller. nothing should be sent.

it returns a json object:
```json
{
    "exec": 0,
    "lender": 0,
    "renter": 0,
    "lambda": 0.2,
    "rec_mu": 0.05,
    "qos_real": 0.99
}
```

the meaning of each field:
- `exec`: the number of exectant containers in pool
- `lender`: the number of lender contaienrs in pool
- `renter`: the number of renter containers in pool
- `lambda`: the lambda value used in idle container identification
- `rec_mu`: the reciprocal of mu used in idle container identification
- `qos_real`: the r_real used in idle container identification

### end
end the proxy server. nothing shoud be sent. return `200 OK` if success.

the proxy server will wait for all requset to be done and then stop itself.