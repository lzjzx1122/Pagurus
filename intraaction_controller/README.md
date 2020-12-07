# Intra-action Controller

## Initialization
when proxy server starts, it will do some initialization jobs:
1. read the config file `action_config.yaml`

config file should have the following form:
```yaml
max_container: 10
actions:
  - name: test_action1
    image: test_img1
    qos_time: 100
    qos_requirement: 0.99
  - name: test_action2
    image: test_img2
    qos_time: 200
    qos_requirement: 0.95
```

the meaning of each field:
- `action`: the name of action
- `image`: the base image name for this action
- `QOS_time`: the maximum time by QOS, in seconds
- `QOS_requirement`: the precent of requests satisfying the QOS requirement
- `max_container`: the maximum number of containers that this action's controller can create

## API
proxy server runs at port 5000. it receives the following requests:
- `/<action_name>/repack`: POST request. tell the controller the pack image has been changed.
- `/<action_name>/run`: POST request. return a json. send a user request to run the action.
- `/<action_name>/lend`: GET request. return a json. get a lender container.
- `/<action_name>/status`: GET request. return a json. get the status of controller.

`action_name` is the actual name of action being called. 

### repack
inform intra-action controller that pack image has been changed. controller will removes all lender containers since they are uesless now.

nothing need to be sent. return `200 OK` if success.

### run
send the request to a container to actually run the code once.

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

### lend
get a lender container from controller. nothing should be sent.

it returns `404 no lender` if no lender container is available.

if there's available lender container, controller remove this container from its pool and return a json object:
```json
{
    "id": XXX,
    "port": 30000
}
```

the meaning of each field:
- `id`: the docker long id of this container
- `port`: the port number this container uses

### status
get the current status of controller. nothing should be sent.

it returns a json object:
```json
{
    "name": "actionname"
    "exec": 0,
    "lender": 0,
    "renter": 0,
    "lambda": 0.2,
    "rec_mu": 0.05,
    "qos_real": 0.99
}
```

the meaning of each field:
- `name`: the action name
- `exec`: the number of exectant containers in pool
- `lender`: the number of lender contaienrs in pool
- `renter`: the number of renter containers in pool
- `lambda`: the lambda value used in idle container identification
- `rec_mu`: the reciprocal of mu used in idle container identification
- `qos_real`: the r_real used in idle container identification

### end
end the proxy server. nothing shoud be sent. return `200 OK` if success.

the proxy server will wait for all requset to be done and then stop itself.