import csv
import numpy as np
import random
import yaml
import json
import sys
import os

action = 'disk'
lender = 'markdown2html'
id = 1

create_pool = [2.463992596,2.36307478,2.355466843,2.513594627,2.483490944,2.394780397,2.57682395,2.306794405,2.525532722,2.421052933,2.544313669,2.305456161,2.43568635,2.457998753,2.56636548,2.393636703,2.253372431,2.288981199,2.819756508,2.316534281,2.439966917,2.563033104,2.380099535,2.342388868,2.30294919,2.203225136,2.248551369,2.499803543,2.455024004,2.220887184,2.271633863,2.360773563,2.468569756,2.327506304,2.86687088]
rent_pool = [0.024842501,
0.021135807,
0.024309635,
0.021949768,
0.021944761,
0.021537781,
0.023271084,
0.022393465,
0.022258997,
0.022017241,
0.021005392,
0.022277594,
0.022519112,
0.021678686,
0.020733118,
0.019746304,
0.021015167,
0.023515224,
0.021878004,
0.022083998,
0.020437241,
0.02856636,
0.021598816,
0.019456148,
0.023525]

def get_create():
    return create_pool[random.randrange(0, len(create_pool))]

def get_rent():
    return rent_pool[random.randrange(0, len(rent_pool))]

keys = ['queue_time', 'create_time', 'rent_time', 'inter_start', 'inter_end', 'end-to-end', 'container_start', 'container_end', 'exeuction']
rows = []
filename = 'results/' + lender + '/' + str(id) + '/' + 'results.csv'
with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['action'] == action:
            tmp = row.copy()
            for k in keys:
                tmp[k] = float(tmp[k])
            if tmp['container_way'] == 'rent':
                tmp['rent_time'] = get_rent()
                tmp['create_time'] = 0
            elif tmp['container_way'] == 'create':
                tmp['rent_time'] = 0
                tmp['create_time'] = get_create()
            tmp['end-to-end'] = tmp['queue_time'] + tmp['rent_time'] + tmp['create_time'] + tmp['exeuction'] + 2.570
            rows.append(tmp)

rows_ = []
filename = 'results/' + lender + '/' + str(id) + '_/' + 'results.csv'
with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['action'] == action:
            tmp = row.copy()
            for k in keys:
                tmp[k] = float(tmp[k])
            if tmp['container_way'] == 'rent':
                tmp['rent_time'] = get_rent()
                tmp['create_time'] = 0
            elif tmp['container_way'] == 'create':
                tmp['rent_time'] = 0
                tmp['create_time'] = get_create()
            tmp['end-to-end'] = tmp['queue_time'] + tmp['rent_time'] + tmp['create_time'] + tmp['exeuction'] + 2.570
            rows_.append(tmp)

file_name = 'results/' + action + '.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'action', 'start_way', 'container_attr', 'container_way', \
        'queue_time', 'create_time', 'rent_time', 'inter_start', \
        'inter_end', 'end-to-end', 'container_start', 'container_end', 'exeuction']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)        

file_name = 'results/' + action + '_.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id', 'action', 'start_way', 'container_attr', 'container_way', \
        'queue_time', 'create_time', 'rent_time', 'inter_start', \
        'inter_end', 'end-to-end', 'container_start', 'container_end', 'exeuction']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows_:
        writer.writerow(row)       