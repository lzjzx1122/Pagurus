import csv
import numpy as np
import random
import yaml
import json
import sys
import os

action = 'disk'
id = 2

dir = 'results_/' + action + '/' + str(id) + '/' + 'set.json' 
exper = json.loads(open(dir, encoding='utf-8').read())
invo = exper[0]['invo']   
print('invo:', len(invo))
        
file_name = 'results/load.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['time', 'load', 'container']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(0, 1440):
        row = {'time': i, 'load': invo[i], 'container': 0}
        writer.writerow(row)