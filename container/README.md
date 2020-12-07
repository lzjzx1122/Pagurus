# proxy server in container

## filesystem structure
- `/proxy/exec/`: the dir where extracted files stay
- `/proxy/exec/main.py`: the default main program of action
- `/proxy/ActionRunner.py`: the proxy server

the working directory of proxy server should be `/proxy/exec/`

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
    "action": "test"
}
```

the meaning of each field:
- action: the action name. action's code should be placed first in directory `/proxy/exec`.

### run
must send a json object. it will be used as the input of the action.
