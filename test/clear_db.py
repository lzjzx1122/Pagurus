import couchdb
import sys

couch = couchdb.Server('http://127.0.0.1:5984/')
db = couch['action_results']
#r = int(sys.argv[1])
for id in db:
 #   if int(id) <= r:
    db.delete(db[id])
    #    print(doc)
