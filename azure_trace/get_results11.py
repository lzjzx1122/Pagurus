import csv
import numpy as np
import random
import yaml
import json
import sys
import os

action = 'video'
id = 3

dir = 'results_/' + action + '/' + str(id) + '/' + 'set.json' 
exper = json.loads(open(dir, encoding='utf-8').read())
invo = exper[0]['invo']   

print('invo:', len(invo))

containers = {}
dir = 'results_/' + action + '/' + str(id) + '_/' + 'container.csv' 
with open(dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:  
        tm = int(row['time'])
        containers[tm] = int(row['exec'])
        
T = 1610077472
file_name = 'results/video.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['time', 'load', 'container']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(377, 1440):
        tm = i - 377 + T
        if tm in containers:
            row = {'time': tm, 'load': invo[i], 'container': containers[tm]}
        else:
            row = {'time': tm, 'load': invo[i], 'container': -1}
        writer.writerow(row)