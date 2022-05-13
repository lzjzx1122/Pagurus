import pandas as pd 
import numpy as np
import csv
import json
import sys
import pandas

dir = sys.argv[1]

# generate cold_start.csv
def get_cold(option):
    res_file = dir + str(option) + '/result.csv'
    df = pd.read_csv(res_file)
    res = {}
    for idx, row in df.iterrows():
        action = row['action']
        if row['start'] == 'cold':
            if action not in res:
                res[action] = 0
            res[action] += 1
    return res

openwhisk = get_cold('openwhisk')
pagurus = get_cold('pagurus')

openwhisk_total, pagurus_total = 0, 0
rows = []
for i in range(1, 389):
    action = i
    openwhisk_cold = openwhisk[action] if action in openwhisk else 0
    pagurus_cold = pagurus[action] if action in pagurus else 0
    openwhisk_total += openwhisk_cold
    pagurus_total += pagurus_cold
row = {'action': 'all', 'openwhisk': openwhisk_total, 'pagurus': pagurus_total}
rows.append(row)   
for i in range(1, 389):
    action = i
    openwhisk_cold = openwhisk[action] if action in openwhisk else 0
    pagurus_cold = pagurus[action] if action in pagurus else 0
    row = {'action': action, 'openwhisk': openwhisk_cold, 'pagurus': pagurus_cold}
    rows.append(row)

file_name = dir + '/cold_start.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)



# generate e2e_latency.csv
def get_latency(option):
    res_file = dir + str(option) + '/result.csv'
    df = pd.read_csv(res_file)
    res = {}
    for idx, row in df.iterrows():
        action = row['action']
        if row['start'] == 'cold':
            if action not in res:
                res[action] = []
            res[action].append(float(row['end2end latency']))
    return res
                        
def div(a, b):
    if a == None or b == None:
        return None
    else:
        return a / b

openwhisk = get_latency('openwhisk')
pagurus = get_latency('pagurus')

rows = []
for i in range(1, 389):
    action = i
    openwhisk_mean = openwhisk[action][max(0, int(0.95 * len(openwhisk[action])) - 1)] if action in openwhisk else None
    pagurus_mean = pagurus[action][max(0, int(0.95 * len(pagurus[action])) - 1)]  if action in pagurus else None
    row = {'action': action, 'openwhisk': openwhisk_mean, 'pagurus': pagurus_mean, 'pagurus/openwhisk': div(pagurus_mean, openwhisk_mean)}
    rows.append(row)

file_name = dir + '/e2e_latency.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'pagurus/openwhisk']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

