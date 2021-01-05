import csv
import numpy as np
import random
import yaml
import json
import sys
import os

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

actions = ["markdown2html", "video", "float_operation", "k-means", "matmul", "image", "map_reduce", "network", "linpack", "disk", "couchdb_test"]
rows = []
for lender in actions:
    for i in range(1, 11):
        filename = 'results/' + lender + '/' + str(i) + '/set.json'
        exper = json.loads(open(filename, encoding='utf-8').read())
        res = {'action': lender, 'id': i, 'runtime': functions[exper[0]['func']]['aver']}
        dir = 'results/' + lender + '/' + str(i) + '/statistic.csv'
        with open(dir, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print('row:', row, row['action'])
                action = str(row['action'])
                if action == lender:
                    res['cold'] = int(row['cold'])
        dir = 'results/' + lender + '/' + str(i) + '_/statistic.csv'
        with open(dir, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action = str(row['action'])
                if action == lender:
                    res['cold_'] = int(row['cold'])
                    res['percentage'] = res['cold'] / res['cold_']
        rows.append(res)

file_name = 'results8.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'id', 'runtime', 'cold', 'cold_', 'percentage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)