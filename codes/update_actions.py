import couchdb
from couchdb import ResourceNotFound
import os


couch = couchdb.Server("http://openwhisk:openwhisk@127.0.0.1:5984")

try:
    couch.delete("my_actions")
except ResourceNotFound:
    pass

db = couch.create("my_actions")

action_path = "/home/openwhisk/pagurus/actions"
action_name_list = os.listdir(action_path)

for action_name in action_name_list:
    db[action_name] = {}
    start_path = os.path.join(action_path, action_name)
    
    for root, dirs, files in os.walk(start_path):
        for fname in files:
            abs_path = os.path.join(root, fname)

            with open(abs_path, 'rb') as f:

                print(abs_path)

                file_path = os.path.relpath(abs_path, start_path)
                if file_path[0] == '_':
                    file_path = "db" + fname # couchdb的attachment不支持'_'开头……

                db.put_attachment(db[action_name], f, filename=file_path)


for row in db.view('_all_docs'):
     print(db[row.id])
