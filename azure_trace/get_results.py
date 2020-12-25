import couchdb
import csv
import sys

url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
server = couchdb.Server(url)
inter = server['inter_results']
intra = server['action_results']


inter_data = {}
for id in inter:
    inter_data[id] = dict(inter[id])

rows = []
for id in intra:
    intra_doc = dict(intra[id])
    inter_doc = dict(inter_data[id])
    # if 'action' not in intra_doc:
        # print(intra_doc)
    row = {'id': id, 'action': intra_doc['action_name'], 'start_way': intra_doc['start_way'], \
        'container_way': intra_doc['container_way'], 'queue_time': intra_doc['queue_time'], \
        'create_time': intra_doc['create_time'], 'rent_time': intra_doc['rent_time'], \
        'inter_start': inter_doc['start'], 'inter_end': inter_doc['end'], \
        'end-to-end': inter_doc['end-to-end'], 'container_start': intra_doc['start_time'], 'container_end': intra_doc['end_time'], 'exeuction': intra_doc['duration']}
    rows.append(row)
rows = sorted(rows, key = lambda i: (i['inter_start'], i['inter_end']))

file_name = sys.argv[1]
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'action', 'start_way', 'container_way', \
        'queue_time', 'create_time', 'rent_time', 'inter_start', \
        'inter_end', 'end-to-end', 'container_start', 'container_end', 'exeuction']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)