import couchdb
import csv
import sys
import json

# result.csv

url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
server = couchdb.Server(url)
inter = server['inter_results']
intra = server['intra_results']

print('Begin Reading Database...')
inter_data = {}
print(len(inter))
for id in inter:
    inter_data[id] = dict(inter[id])
print('Read End')

dir = sys.argv[1]

rows = []
for id in intra:
    intra_doc = dict(intra[id])
    if id not in inter_data:
        print(intra_doc['action_name'])
        continue
    inter_doc = dict(inter_data[id])
    row = { 'id': id, 'action': intra_doc['action_name'], 'intra_latency': intra_doc['intra_latency'], 'start_way': intra_doc['start_way'], 'container_attr': intra_doc['container_attr'], \
        'container_way': intra_doc['container_way'], 'queue_time': intra_doc['queue_time'], \
        'create_time': intra_doc['create_time'], 'rent_time': intra_doc['rent_time'], \
        'inter_start': inter_doc['start'], 'inter_end': inter_doc['end'], \
        'end-to-end': inter_doc['end-to-end'], 'container_start': intra_doc['start_time'], \
            'container_end': intra_doc['end_time'], 'exeuction': intra_doc['duration']}
    rows.append(row)
rows = sorted(rows, key = lambda i: (i['inter_start'], i['inter_end']))

start = float(rows[0]['inter_start'])

new_rows = []
for row in rows:
    relative = float(row['inter_start']) - start
    if relative >= 3599:
        queue = float(row['queue_time'])
        rent = float(row['rent_time'])
        create = float(row['create_time'])
        # intra = queue + rent + create
        # inter = float(row['end-to-end']) - float(row['exeuction'])
        exe = queue + rent + create + float(row['exeuction'])
        new_rows.append({'action': row['action'], 'start': row['start_way'], 'container': row['container_way'], 'create_time': row['create_time'], 'rent_time': row['rent_time'], 'end2end latency': exe, 'time_from_system_start': relative})

file_name = dir + '/result.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'start', 'container', 'create_time', 'rent_time', 'end2end latency', 'time_from_system_start']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in new_rows:
        writer.writerow(row)
