# Pagurus
part of code
The steps to run:
- `cd recode/controller`
- Open terminal 1
  `export FLASK_APP=action_listening.py`
  `python3 -m flask run`
- Open terminal 2
  `python3 class_controller.py`
- Open terminal 3
  Send requests to the server.
  For example, `curl -X POST "http://127.0.0.1:5000/listen" -d '{"action_name":"linpack", "max_containers": 10}'`

