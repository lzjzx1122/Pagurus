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
renter_res_before = {"markdown2html":0, "video":0, "float_operation":0, "k-means":0, "matmul":0, "image":0, "map_reduce":0, "network":0, "linpack":0, "disk":0, "couchdb_test":0}
renter_res_after = {"markdown2html":0, "video":0, "float_operation":0, "k-means":0, "matmul":0, "image":0, "map_reduce":0, "network":0, "linpack":0, "disk":0, "couchdb_test":0}
action_total_res =  {"markdown2html":[], "video":[], "float_operation":[], "k-means":[], "matmul":[], "image":[], "map_reduce":[], "network":[], "linpack":[], "disk":[], "couchdb_test":[]}

def add_renter_res(renter_res):
    global renter_total_res
    for action in actions:
        renter_total_res[action] += renter_res[action]


for lender in actions:
    for i in iterations[lender]:
        # print(lender, i)
        dir = 'results/' + lender + '/' + str(i) + '/statistic.csv'
        total_cold = 0
        total_warm = 0
        with open(dir, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print('row:', row, row['action'])
                action = str(row['action'])
                cold = int(row['cold'])
                warm = int(row['warm'])
                total_cold += cold
                total_warm += warm 
                renter_res_after[action] += cold
        dir = 'results/' + lender + '/' + str(i) + '_/statistic.csv'
        total_cold_ = 0
        total_warm_ = 0
        with open(dir, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                action = str(row['action'])
                cold = int(row['cold'])
                warm = int(row['warm'])
                total_cold_ += cold
                total_warm_ += warm 
                renter_res_before[action] += cold
        action_total_res[lender].append(total_cold / total_cold_)
        
'''
file_name = 'results2.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'average']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for action in action_total_res:
        row = {'action': action}
        tmp = 0
        print(action, action_total_res[action])
        for i in range(10):
            row[str(i + 1)] = action_total_res[action][i]
            tmp +=  action_total_res[action][i]
        row['average'] = tmp / 10
        writer.writerow(row)
print("---------------------------------------------")
'''
for action in actions:
    print(action, ',', 1 - renter_res_after[action] / renter_res_before[action])

