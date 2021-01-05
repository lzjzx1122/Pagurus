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
with open('function_durations_percentiles.anon.d07.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        function = row['HashFunction']
        average = float(row['Average'])
        count = int(row['Count'])
        minimum = float(row['Minimum'])
        maximum = float(row['Maximum'])
        functions.append({'function': function, 'aver': average, 'count': count, 'min': minimum, 'max': maximum})


# Divide the whole range into 11 parts.
total = len(functions)
print('total_line:', total)
M = total / 11
L, R = [], []
for i in range(11):
    L.append(round(i * M))
for i in range(10):
    R.append(L[i + 1] - 1)
R.append(total - 1)


# Shuffle the order of actions. 
lender = sys.argv[1]
actions = ["linpack", "image", "network", "float_operation", "disk", "video", "matmul", "map_reduce", "couchdb_test", "markdown2html", "k-means"]
actions.remove(lender)
random.shuffle(actions)
actions.append(lender)


# Random in every range
while True:
    selected_id = []
    selected_func = []
    selected_count = []
    selected_aver = []
    selected_invo = [None] * 11
    for i in range(11):
        selected_id.append(random.randrange(L[i], R[i]))
        # print(selected_id)
        selected_func.append(functions[selected_id[i]]['function'])
        selected_count.append(functions[selected_id[i]]['count'])
        selected_aver.append(functions[selected_id[i]]['aver'])
    flag = True
    with open('invocations_per_function_md.anon.d07.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for i in range(11):
                if row['HashFunction'] == selected_func[i]:
                    tmp = []
                    for col in range(1, 1441):
                        tmp.append(int(row[str(col)]))
                    selected_invo[i] = tmp
                    if sum(tmp) > 100000:
                        flag = False
    for i in range(11):
        if selected_invo[i] == None:
            flag = False
    if flag == True:
        break


'''
for j in range(1440):
    for i in range(11):
        print(selected_invo[i][j], end = ' ')
    print('')
'''
os.system('mkdir ' + sys.argv[2])

# Generate action_config.yaml for the intra-controller.
actions_config = []
for i in range(11):
    name = actions[10 - i]
    actions_config.append({'name': name, 'image': 'action_' + name, 'qos_time': qos_target(selected_aver[i] / 1000 / 60), 'qos_requirement': 0.95})
action_config = {'max_container': 10, 'actions': actions_config}
#f = open('/home/openwhisk/gls/intraaction_controller/action_config.yaml', 'w', encoding = 'utf-8')
#yaml.dump(action_config, f)
os.system('touch ' + sys.argv[2] + '/action_config.yaml')
f = open(sys.argv[2] + '/action_config.yaml', 'w', encoding = 'utf-8')
yaml.dump(action_config, f)


# Generate experiment set
exper = []
for i in range(11):
    exper.append({'name': actions[10 - i], 'id': selected_id[i], 'runtime': max(0.006, selected_aver[i] / 1000 / 60),\
        'func': selected_func[i], 'count': sum(selected_invo[i]), 'invo': selected_invo[i]})
os.system('touch ' + sys.argv[2] + '/set.json')
f = open(sys.argv[2] + '/set.json', 'w', encoding = 'utf-8')
json.dump(exper, f, sort_keys = False, indent = 4)

