import csv
import numpy as np
import random
import yaml
import json
import sys
import os
import json

# Read csv file.
functions = {}
with open('function_durations_percentiles.anon.d07.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        function = row['HashFunction']
        average = float(row['Average'])
        count = int(row['Count'])
        minimum = float(row['Minimum'])
        maximum = float(row['Maximum'])
        functions[function] = {'aver': average, 'count': count, 'min': minimum, 'max': maximum}

actions = ["video", "markdown2html", "float_operation", "k-means", "matmul", "image", "map_reduce", "network", "linpack", "disk", "couchdb_test"]
res = {}
for action in actions:
    for id in range(1, 7):
        rows = []
        filename = 'results/' + action + '/' + str(id) + '/' + 'results.csv'
        exper = json.loads(open('results/' + action + '/' + str(id) + '/' + 'set.json', encoding='utf-8').read())
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action_ = row['action']
                if row['container_way'] == 'queue' or row['container_way'] == 'create':
                    continue
                if action_ == action:
                    rows.append(float(row['end-to-end']) - float(row['exeuction']))
                    # print(row['container_way'], float(row['end-to-end']) - float(row['exeuction']))
        rows = sorted(rows)
        total = len(rows)
        # print('total:', total)
        rows = rows[:-int(total * 0.1)]
        if len(rows) > 0:
            res[action + str(id)] = {'action': action, 'id':id, 'count': len(rows), 'min_startup': rows[0], 'max_startup': rows[-1], 'average_startup': sum(rows) / len(rows), 'execution': float(functions[exper[0]['func']]['aver']) / 1000}

file_name = 'results3.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'id', 'count', 'min_startup', 'max_startup', 'average_startup', 'execution']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in res.values():
        writer.writerow(row)