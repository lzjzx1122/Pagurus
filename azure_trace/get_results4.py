import csv
import numpy as np
import random
import yaml
import json
import sys
import os

actions = ["markdown2html", "video", "float_operation", "k-means", "matmul", "image", "map_reduce", "network", "linpack", "disk", "couchdb_test"]
iterations = {'markdown2html': [1, 2, 4, 5, 6, 8, 9, 10], 
              'video': [1, 2, 3, 5, 6, 7, 8, 10],
              'float_operation': [2, 3, 4, 5, 6, 7, 9, 10],
              'k-means': [2, 3, 4, 5, 7, 8, 9, 10],
              'matmul': [1, 2, 3, 4, 5, 6, 7, 8],
              'image': [1, 3, 5, 6, 7, 8, 9, 10],
              'map_reduce': [7, 8, 9, 10],
              'network': [1, 3, 4, 5, 6, 8, 9, 10],
              'linpack': [1, 2, 3, 4, 5, 6, 7, 10],
              'disk': [1, 2, 3, 4, 5, 6, 7, 10],
              'couchdb_test': [6, 7, 8, 9, 10]}

containers = {}
for action in actions:
    rows = []
    for id in iterations[action]:
        filename = 'results/' + action + '/' + str(id) + '/' + 'statistic.csv'
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action_ = row['action']
                if action_ == 'map_reduce':
                    print(action, id, 'create:', int(row['create']), 'rent:', int(row['rent']))
                if action_ not in containers.keys():
                    containers[action_] = {'total':0, 'rent':0}
                containers[action_]['total'] += int(row['create']) + int(row['rent'])
                containers[action_]['rent'] += int(row['rent'])
  
'''
file_name = 'results/results4.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'rent', 'total', 'percentage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for action in containers.keys():
        rent = containers[action]['rent']
        total = containers[action]['total']
        row = {'action':action, 'rent':rent, 'total':total, 'percentage':rent/total}
        writer.writerow(row)
'''