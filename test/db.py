import couchdb

import sys



couch = couchdb.Server('http://172.23.164.203:5984/')

db = couch['action_results']





queue = {}

create = {}

rent = {}

duration = {}



for id in db:

        doc = db[id]

        name = doc['action_name']

        if name == sys.argv[1]:

                continue

        if name not in queue:

                queue[name] = []

                create[name] = []

                rent[name] = []

                duration[name] = []



        queue[name].append(doc['queue_time'])

        create[name].append(doc['create_time'])

        rent[name].append(doc['rent_time'])

        duration[name].append(doc['duration'])



for name in create:

        print("-------------------------------------")

        print(name)

        for x in create[name]:

                print(x)

        print("")



        for x in queue[name]:

                print(x)

        print("")



        for x in rent[name]:

                print(x)

        print("")



        for x in duration[name]:

                print(x)

        print("")


