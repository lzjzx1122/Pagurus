import csv
import numpy as np
import random

functions = dict()
with open('function_durations_percentiles.anon.d01.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        functions[]
        function = row['HashFunction']
        average = int(row['Average'])
        count = int(row['Count'])
        minimum.append(int(row['Minimum']))
        maximum.append(int(row['Maximum']))
        
print('total_line:', len(average))

inv_func, inv = [], []
with open('invocations_per_function_md.anon.d01.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tmp = []
        for i in range(1, 1441):
            tmp.append(int(row[str(i)]))
        inv.append(tmp)
        inv_func.append(row['HashFunction'])

M = len(average) / 11
L, R = [], []
for i in range(11):
    L.append(round(i * M))
for i in range(10):
    R.append(L[i + 1] - 1)
R.append(len(average) - 1)

# random.seed(0)
for i in range(11):
    selected = random.randrange(L[i], R[i])


