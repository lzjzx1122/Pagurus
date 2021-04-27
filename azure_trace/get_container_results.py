import csv
import couchdb
import sys

url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
server = couchdb.Server(url)
memory = server['container']
rows = []
for id in memory:
    doc = dict(memory[id])
    row = {'id': id, 'action': doc['action'], 'time': doc['time'], 'exec': doc['exec'], 'lender': doc['lender'], 'renter': doc['renter']}
    rows.append(row)
file_name = sys.argv[1] + '/container.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'action', 'time', 'exec', 'lender', 'renter']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)