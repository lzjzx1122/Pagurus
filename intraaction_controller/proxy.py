from gevent import monkey
monkey.patch_all()
import docker
import sys
import json
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import action
import file_controller

proxy = Flask(__name__)
proxy.debug = False
server = None

couchdb_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
db_name = 'action_results'

@proxy.route('/<action_name>/repack', methods=['POST'])
def repack(action_name):
    if action_name not in action.all_action:
        return ('NOT FOUND', 404)
    action.all_action[action_name].remove_lender()
    return ('OK', 200)

@proxy.route('/<action_name>/run', methods=['POST'])
def run(action_name):
    data = request.get_json(force=True, silent=True)
    if action_name not in action.all_action:
        return ('NOT FOUND', 404)
    action.all_action[action_name].send_request(data['request_id'], data['data'])
    return ('OK', 200)

@proxy.route('/<action_name>/lend', methods=['GET'])
def lend(action_name):
    if action_name not in action.all_action:
        return ('NOT FOUND', 404)

    res = action.all_action[action_name].giveout_container()
    if res is None:
        return ('no lender', 403)
    else:
        return (json.dumps({"id": res[0], "port": res[1]}), 200)

@proxy.route('/<action_name>/status', methods=['GET'])
def status(action_name):
    return action.all_action[action_name].pool_status()

@proxy.route('/end', methods=['POST'])
def end():
    action.end()
    global server
    server.stop()
    return ('OK', 200)

def main():
    global server
    file_controller.init('/home/openwhisk/gls/interaction_controller/actions/', '/var/run/pagurus/')
    action.init('/home/openwhisk/gls/intraaction_controller/action_config.yaml', (15000, 20000), couchdb_url, db_name)
    server = WSGIServer(('0.0.0.0', int(sys.argv[1])), proxy)
    server.serve_forever()

if __name__ == '__main__':
    main()
