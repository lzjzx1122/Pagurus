import couchdb
import csv
import sys

url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
server = couchdb.Server(url)
lend_info = server['lend_info']


rows = []
for id in lend_info:
    doc = dict(lend_info[id])
    row = {'id': id, 'time': doc['time'], 'action': doc['action'], 'qos': doc['qos'], 'qos_target': doc['qos_target'], 'num_lender': doc['num_lender']}
    rows.append(row)
rows = sorted(rows, key = lambda i: (i['time']))


file_name = sys.argv[1]
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'time', 'action', 'qos', 'qos_target', 'num_lender']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)