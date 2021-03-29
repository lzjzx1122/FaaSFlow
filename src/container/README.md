# proxy server in container

## API
server runs at port 5000 in the container. it receives the following request:
- `/status`: GET request. return a json. get the status including `new`, `init`, `run`, and `ok`. the action name is sended after init.
- `/init`: POST request. do the initialization like decrypting and extracting.
- `/run`: POST request. return a json. to actually run the action.


### status
the meaning of each status:
- new: a new container before doing init
- init: currently doing the initialization
- run: currently handling a request
- ok: wait for a request

### init
must send a json object in the following form:
```json
{
    "action": "test",
    "pwd": "test"
}
```

the meaning of each field:
- action: the action name. it's used to find the filename of its zipfile.
- pwd: the passphrase to extract its zipfile. it's not stored in container to keep security.

### run
must send a json object. it will be used as the input of the action.

## structure of action zipfile
the action zipfile should contain a python file `main.py`, which will be executed when a request comes.
the default entry point of `main.py` is `main()` function.