import csv
import numpy as np
import random
import yaml
import json
import sys
import os

rows = []
dir = '/home/openwhisk/gls/azure_trace/results_/image/2/container.csv'
with open(dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rows.append(row)

rows.sort(key=lambda k: (k.get('time', 0)))

rows_ = []    
cnt = 0
for row in rows:
    if cnt % 11 == 3:        
        rows_.append(row)
    cnt += 1

file_name = 'results/map_reduce.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['id','time','exec','lender','renter']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows_:
        writer.writerow(row)