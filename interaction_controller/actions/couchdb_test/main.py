import couchdb
from couchdb import PreconditionFailed
import os
import random
import time

def main(params):
        
    start = time.time()

    couch = couchdb.Server("http://openwhisk:openwhisk@10.2.64.8:5984")
    #couch = couchdb.Server("http://127.0.0.1:5984")

    while True:
        try:
            dbname = "test" + str(random.randint(0,999999))
            db = couch.create(dbname)
            break
        except PreconditionFailed:
            pass

    # print("------------------------------------cwd-----------------------------------")
    # print(os.getcwd())
    action_path = '/proxy/exec/couchdb_test/actions'
    #action_path = 'actions' #os.path.join(os.getcwd(), 'actions')
    action_name_list = os.listdir(action_path)

    # print("____________________________________ok___________________________________")

    for action_name in action_name_list:
        db[action_name] = {}
        start_path = os.path.join(action_path, action_name)
        
        for root, dirs, files in os.walk(start_path):
            for fname in files:
                abs_path = os.path.join(root, fname)

                with open(abs_path, 'rb') as f:

                    # print(abs_path)

                    file_path = os.path.relpath(abs_path, start_path)
                    if file_path[0] == '_':
                        file_path = "db" + fname # couchdb的attachment不支持'_'开头……

                    db.put_attachment(db[action_name], f, filename=file_path)


    # for row in db.view('_all_docs'):
    #     print(db[row.id])

    couch.delete(dbname)

    print("Latency:", time.time() - start)
