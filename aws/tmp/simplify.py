import couchdb
import csv
import sys
import json
import pandas as pd


filename = sys.argv[1] + '/results.csv'
df = pd.read_csv(filename)
start = float(df['inter_start'][0])
new_rows = []

for idx, row in df.iterrows():
    if row['container_way'] == 'create' or row['container_way'] == 'rent' or row['container_way'] == 'prewarm':
        new_rows.append({'action': row['action'], 'start': row['start_way'], 'container': row['container_way'], 'create_time': row['create_time'], 'rent_time': row['rent_time'], 'end2end latency': row['intra_latency'], 'time_from_system_start': float(row['inter_start']) - start})

file_name = sys.argv[1] + '/result.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'start', 'container', 'create_time', 'rent_time', 'end2end latency', 'time_from_system_start']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in new_rows:
        writer.writerow(row)

