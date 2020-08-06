import couchdb
import time
from flask import Flask, request

# a Flask instance.
proxy = Flask(__name__)
couch = couchdb.Server("http://openwhisk:openwhisk@localhost:5984/")
db_requests = couch.create("action_requests")

# listen user requests
@proxy.route('/listen', methods=['POST'])
def listen():
    inp = request.get_json(force=True, silent=True)
    action_name = inp['action_name']
    max_containers = inp['max_containers']
    arrival_time = time.time()
    
    doc = {'action_name':action_name, 'max_containers':max_containers, 'arrival_time':arrival_time}
    db_requests.save(doc)
    
    return "ok"
