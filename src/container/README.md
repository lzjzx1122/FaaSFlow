# proxy server in container

## structure
- `/proxy/actions/`: the zip files of actions
- `/proxy/actions/action_ABC.zip`: encrypted zip file of action ABC
- `/proxy/exec/`: the dir where extracted files stay
- `/proxy/exec/main.py`: the default main program of action
- `/proxy/ActionRunner.py`: the proxy server

the working directory of proxy server should be `/proxy/exec/`

## API
server runs at port 5000 in the container. it receives the following request:
- `/status`: GET request. return a json. get the status including `new`, `init`, `run`, and `ok`. the action name is sended after init.
- `/init`: POST request. do the initialization like decrypting and extracting.
- `/run`: POST request. return a json. to actually run the action.
- `/inject`: POST request. inject the action code (a zip file) into the container.

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

### inject
must send a json object containing the name of the action and base64 encode of the zipfile.
```json
{
    "action": "test",
    "zipfile": "(base64 encode of the zipfile)"
}
```

the meaning of each field:
- action: the action name.
- zipfile: the base64 encode of action's zipfile. the zipfile will be named as "action_(action name).zip"

## structure of action zipfile
the action zipfile should contain a python file `main.py`, which will be executed when a request comes.
the default entry point of `main.py` is `main()` function.