import pandas as pd
import numpy as np
import csv
import json
import sys,os
import pandas

for root, dirs, files in os.walk('result-plot/'):
    array = dirs
    if array:
        D = array
        break
D_len = len(D)


# generate cold_start.csv
def get_cold(kind):
    res = {}
    for dir in D:
        filename = 'result-plot/' + str(dir) + '/' + kind + '/result.csv'
        print('now precessing number ', dir , 'for ', kind, 'of file cold_start.csv')
        df = pd.read_csv(filename)
        for idx, row in df.iterrows():
            action = int(row['action'][7:]) * D_len + int(dir)
            if row['start'] == 'cold':
                if action not in res:
                    res[action] = 0
                res[action] += 1
    return res

openwhisk = get_cold('openwhisk')
pagurus = get_cold('pagurus')

openwhisk_total, pagurus_total = 0, 0
rows = []
#for i in range(1, len(openwhisk)):
#    action = i
#    openwhisk_cold = openwhisk[action] if action in openwhisk else 0
#    pagurus_cold = pagurus[action] if action in pagurus else 0
#    openwhisk_total += openwhisk_cold
#    pagurus_total += pagurus_cold
#row = {'action': 'all', 'openwhisk': openwhisk_total, 'pagurus': pagurus_total}
#rows.append(row)   

for action in openwhisk:
    openwhisk_cold = openwhisk[action] if action in openwhisk else 0
    pagurus_cold = pagurus[action] if action in pagurus else 0
    row = {'action': action, 'openwhisk': openwhisk_cold, 'pagurus': pagurus_cold}
    rows.append(row)
rows = sorted(rows,key=lambda x:x['action'])
file_name = 'result-plot/cold_start.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


# generate e2e_latency.csv
def get_latency(kind):
    res = {}
    for dir in D:
        filename = 'result-plot/' + str(dir) + '/' + kind + '/result.csv'
        print('now precessing number ', dir , 'for ', kind, 'of file e2e_latency.csv')
        df = pd.read_csv(filename)
        for idx, row in df.iterrows():
            action = int(row['action'][7:]) * D_len + int(dir)
            #if row['container'] == 'rent' or row['container'] == 'create':
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
for action in openwhisk:
    if action in openwhisk:
        openwhisk[action] = sorted(openwhisk[action])
        openwhisk_mean = openwhisk[action][max(0, int(0.95 * len(openwhisk[action])) - 1)] 
    else:
        openwhisk_mean = None
    if action in pagurus:
        pagurus[action] = sorted(pagurus[action])
        pagurus_mean = pagurus[action][max(0, int(0.95 * len(pagurus[action])) - 1)] 
    else:
        pagurus_mean = None
    
    row = {'action': action, 'openwhisk': openwhisk_mean, 'pagurus': pagurus_mean, 'openwhisk/pagurus': div(openwhisk_mean, pagurus_mean)}
    rows.append(row)

rows = sorted(rows,key=lambda x:x['action'])

file_name = 'result-plot/e2e_latency.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'openwhisk/pagurus']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
