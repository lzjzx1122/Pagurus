import csv
import numpy as np
import random
import yaml
import json
import sys
import os

def qos_target(runtime):
    return max(0.2, runtime * 2)

# Read csv file.
functions = []
with open('functions.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        function = row['HashFunction']
        average = float(row['Average'])
        count = int(row['Count'])
        functions.append({'function': function, 'aver': average, 'count': count})

# Divide the whole range into 11 parts.
total = len(functions)
print('total_line:', total)
Range_number = 3880
M = total / Range_number
L, R = [], []
for i in range(Range_number):
    L.append(round(i * M))
for i in range(Range_number - 1):
    R.append(L[i + 1] - 1)
R.append(total - 1)

one_second = 1

# Random in every range
while True:
    selected_id = []
    selected_func = []
    selected_count = []
    selected_aver = []
    selected_invo = [None] * Range_number
    for i in range(Range_number):
        selected_id.append(random.randrange(L[i], R[i]))
        selected_func.append(functions[selected_id[i]]['function'])
        selected_count.append(functions[selected_id[i]]['count'])
        selected_aver.append(functions[selected_id[i]]['aver'])
    with open('invocations_per_function_md.anon.d07.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for i in range(Range_number):
                if row['HashFunction'] == selected_func[i]:
                    tmp = []
                    for col in range(1, 1441):
                        tmp.append(int(row[str(col)]))
                    selected_invo[i] = tmp
    break
   
os.system('mkdir ' + sys.argv[1])

X = [0 for i in range(1440)]

E = 10
for e in range(E):
    os.system('mkdir ' + sys.argv[1] + '/' + str(e + 1))

    # Generate action_config.yaml for the intra-controller.
    actions_config = []
    for i in range(e, Range_number, E):            
        name = 'utility' + str(round(i / E))
        actions_config.append({'name': name, 'image': 'action_' + name, 'qos_time': qos_target(selected_aver[i] / 1000 / one_second), 'qos_requirement': 0.95})
    action_config = {'max_container': 10, 'actions': actions_config}
    os.system('touch ' + sys.argv[1] + '/action_config.yaml')
    f = open(sys.argv[1] + '/' + str(e + 1) + '/action_config.yaml', 'w', encoding = 'utf-8')
    yaml.dump(action_config, f)

    # Generate experiment set
    exper = []
    for i in range(e, Range_number, E):
        name = 'utility' + str(round(i / E))
        exper.append({'name': name, 'id': selected_id[i], 'runtime': selected_aver[i] / 1000 / one_second,\
            'func': selected_func[i], 'count': sum(selected_invo[i]), 'invo': selected_invo[i]})
        for j in range(1440):
            if int(selected_invo[i][j]) > 0:
                X[j] += 1
    os.system('touch ' + sys.argv[1] + '/set.json')
    f = open(sys.argv[1] + '/' + str(e + 1) + '/set.json', 'w', encoding = 'utf-8')
    json.dump(exper, f, sort_keys = False, indent = 4)

for j in range(1440):
    X[j] /= 3880

# print(X)
