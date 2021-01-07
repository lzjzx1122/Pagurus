import csv
import numpy as np
import random
import yaml
import json
import sys
import os

actions = ["video", "network", "linpack", "disk", "float_operation", "k-means", "markdown2html", "matmul", "image", "map_reduce", "couchdb_test"]
iterations = {"video":[1], "network":[1,3,4], "linpack":[1], "disk":[1], "float_operation":[1], "k-means":[1], "markdown2html":[1], "matmul":[1,2,3,4], "image":[1,2,3,4], "map_reduce":[1,2,3,4], "couchdb_test":[1]}
# Read csv file.
containers_before = {}
containers_after = {}

for action in actions:
    for i in range(1, 2):
        containers_before[action] = 0
        containers_after[action] = 0
        dir = 'results_/' + action + '/' + str(i) + '/' + 'container.csv'
        with open(dir, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                containers_after[action] += int(row['exec']) + int(row['lender']) + int(row['renter'])
        dir = 'results_/' + action + '/' + str(i) + '_/' + 'container.csv'
        with open(dir, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                containers_before[action] += int(row['exec']) + int(row['lender']) + int(row['renter'])

file_name = 'results/results9.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'before', 'after', 'percentage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for action in containers_before.keys():
        row = {'action':action, 'before': containers_before[action], 'after': containers_after[action], 'percentage': containers_after[action] / containers_before[action]}
        writer.writerow(row)