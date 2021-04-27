import csv
import numpy as np
import random
import yaml
import json
import sys
import os

functions_ = set()
with open('invocations_per_function_md.anon.d07.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        functions_.add(row['HashFunction'])
        
functions = []
not_exist = 0
with open('function_durations_percentiles.anon.d07.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        function = row['HashFunction']
        if function not in functions_:
            not_exist += 1
            continue
        average = float(row['Average'])
        count = int(row['Count'])
        if average < 100 or average > 5000 or count >= 100000 or count <= 0:
            continue
        functions.append({'HashFunction': function, 'Average': average, 'Count': count})

print(not_exist)

file_name = 'functions.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['HashFunction', 'Average', 'Count']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in functions:
        writer.writerow(row)