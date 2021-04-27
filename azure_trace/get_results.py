import couchdb
import csv
import sys


# result.csv

url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
server = couchdb.Server(url)
inter = server['inter_results']
intra = server['intra_results']

print('inter begin')
inter_data = {}
print(len(inter))
for id in inter:
    inter_data[id] = dict(inter[id])
print('inter end')

rows = []
for id in intra:
    intra_doc = dict(intra[id])
    if id not in inter_data:
        print(intra_doc['action_name'])
        continue
    inter_doc = dict(inter_data[id])
    row = { 'id': id, 'action': intra_doc['action_name'], 'start_way': intra_doc['start_way'], 'container_attr': intra_doc['container_attr'], \
        'container_way': intra_doc['container_way'], 'queue_time': intra_doc['queue_time'], \
        'create_time': intra_doc['create_time'], 'rent_time': intra_doc['rent_time'], \
        'inter_start': inter_doc['start'], 'inter_end': inter_doc['end'], \
        'end-to-end': inter_doc['end-to-end'], 'container_start': intra_doc['start_time'], \
            'container_end': intra_doc['end_time'], 'exeuction': intra_doc['duration']}
    rows.append(row)
rows = sorted(rows, key = lambda i: (i['inter_start'], i['inter_end']))

file_name = sys.argv[1] + '/results.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'action', 'start_way', 'container_attr', 'container_way', \
        'queue_time', 'create_time', 'rent_time', 'inter_start', \
        'inter_end', 'end-to-end', 'container_start', 'container_end', 'exeuction']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

exit()

# statistic.csv
data = {}
for row in rows:
    action = row['action']
    if action not in data:
        data[action] = {'action': action, 'cold': 0, 'warm': 0, 'create': 0, 'rent': 0, 'queue': 0}
    data[action][row['start_way']] += 1
    data[action][row['container_way']] += 1

file_name = sys.argv[1] + '/statistic.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'cold', 'warm', 'create', 'rent', 'queue']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for (k, v) in data.items():
        writer.writerow(v)


# lender_info.csv
lend_info = server['lend_info']

rows = []
for id in lend_info:
    doc = dict(lend_info[id])
    row = {'id': id, 'time': doc['time'], 'action': doc['action'], 'lender_pool': doc['lender_pool'], 'type': doc['type']}
    rows.append(row)
rows = sorted(rows, key = lambda i: (i['time']))

file_name = sys.argv[1] + '/lender_info.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'time', 'action', 'lender_pool', 'type']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


# renter_lender_info.csv
rent_info = server['renter_lender_info']
rows = []
for id in rent_info:
    doc = dict(rent_info[id])
    row = {'id': id, 'time': doc['time'], 'lender': doc['lender'], 'renter': doc['renter']}
    rows.append(row)
rows = sorted(rows, key = lambda i: (i['time']))

file_name = sys.argv[1] + '/renter_lender_info.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'time', 'lender', 'renter']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

memory = server['overhead']
rows = []
for id in memory:
    doc = dict(memory[id])
    row = {'id': id, 'time': doc['time'], 'inter_memory': doc['inter_memory'], 'intra_memory': doc['intra_memory'], 'inter_cpu': doc['inter_cpu'], 'intra_cpu': doc['intra_cpu']}
    rows.append(row)
file_name = sys.argv[1] + '/overhead.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'time', 'inter_memory', 'intra_memory', 'inter_cpu', 'intra_cpu']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

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

memory = server['zygote_time']
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