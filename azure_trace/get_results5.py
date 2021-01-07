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
        filename = 'results/' + action + '/' + str(id) + '/' + 'lender_info.csv'
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action_ = row['action']
                if action_ not in containers.keys():
                    containers[action_] = {'repacked':0, 'lent':0}
                if row['type'] == 'repack':
                    containers[action_]['repacked'] += 1
        filename = 'results/' + action + '/' + str(id) + '/' + 'renter_lender_info.csv'
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lender = row['lender']
                if lender not in containers.keys():
                    containers[lender] = {'repacked':0, 'lent':0}
                containers[lender]['lent'] += 1
               
file_name = 'results/results5.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'lent', 'repacked', 'percentage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for action in containers.keys():
        repacked = containers[action]['repacked']
        lent = containers[action]['lent']
        row = {'action':action, 'lent':lent, 'repacked':repacked, 'percentage':lent/repacked}
        writer.writerow(row)