import couchdb
from couchdb import ResourceNotFound
import os
import sys


def load_codes(db, action_name, root):
    doc = db[action_name]
    attachments = doc['_attachments']

    for file_path in attachments.keys():
        abs_path = os.path.join(root, action_name, file_path)
        try:
            f = open(abs_path, 'wb')
        except FileNotFoundError:
            os.makedirs(os.path.dirname(abs_path))
            f = open(abs_path, 'wb')
            
        attach_file = db.get_attachment(doc, file_path)
        if attach_file is not None:
            f.write(attach_file.read())
        f.close()

couch = couchdb.Server("http://openwhisk:openwhisk@10.2.64.9:5984")
action_path = "/action"

try:
    db = couch["my_actions"]
except ResourceNotFound:
    pass
else:
    load_codes(db, sys.argv[1], action_path)