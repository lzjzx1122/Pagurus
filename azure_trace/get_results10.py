import csv
import numpy as np
import random
import yaml
import json
import sys
import os

action = 'disk'
id = 3
record = {}
# delta = 1609147292.62095 - 1609144888.70768
# delta = 1609656087.47303 - 1609619196.02604
delta = 1609198912.0094 - 1609113201.26467
dir = 'results/' + action + '/' + str(id) + '/' + 'lender_info.csv'
with open(dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tm = int(float(row['time']))
        if tm not in record:
            record[tm] = {'cold': 0, 'zygote': 0}
        record[tm]['zygote'] += 1

cnt = 0
dir = 'results/' + action + '/' + str(id) + '_/' + 'results.csv'
with open(dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tm = int(float(row['inter_start']) + delta)
        if row['start_way'] == 'cold':
            if tm not in record:
                record[tm] = {'cold': 0, 'zygote': 0}
            # print('cold:', tm)
            cnt += 1
            record[tm]['cold'] += 1

min_tm = 1000000000000
max_tm = 0
for tm in record.keys():
    min_tm = min(min_tm, tm)
    max_tm = max(max_tm, tm)
    

file_name = 'results/disk_result.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['time', 'cold', 'zygote']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for tm in range(min_tm, max_tm + 1):
        row = {}
        if tm in record.keys():
            row = {'time': tm, 'cold': record[tm]['cold'], 'zygote': record[tm]['zygote']}
        else:
            row = {'time': tm, 'cold': 0, 'zygote': 0}
        writer.writerow(row)