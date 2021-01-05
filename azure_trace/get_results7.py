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

actions = ['video', 'network', 'matmul', 'markdown2html', 'map_reduce', 'linpack', 'image', 'k-means', 'float_operation', 'disk', 'couchdb_test']
rows = []
for action in actions:
    for i in range(1, 9):
        filename = 'results/' + action + '/' + str(i) + '/set.json'
        exper = json.loads(open(filename, encoding='utf-8').read())
        res = {'action': action, 'id':i}
        filename = 'results/' + action + '/' + str(i) + '/statistic.csv'
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action_ = row['action']
                if action_ == action:
                    res['cold'] = row['cold']
                    res['runtime'] = functions[exper[0]['func']]['aver']
        filename = 'results/' + action + '/' + str(i) + '_/statistic.csv'
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action_ = row['action']
                if action_ == action:
                    res['cold_'] = row['cold']
                    res['percentage'] = float(res['cold']) / float(res['cold_'])
        rows.append(res)

file_name = 'results7.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'id', 'cold', 'cold_', 'runtime', 'percentage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)        