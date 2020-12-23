import csv
import numpy as np
import random

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

total = len(functions)
print('total_line:', total)
M = total / 11
L, R = [], []
for i in range(11):
    L.append(round(i * M))
for i in range(10):
    R.append(L[i + 1] - 1)
R.append(total - 1)

while True:
    selected_id = []
    selected_func = []
    selected_count = []
    selected_aver = []
    selected_invo = [None] * 11
    for i in range(11):
        selected_id.append(random.randrange(L[i], R[i]))
        selected_func.append(functions[selected_id[i]]['function'])
        selected_count.append(functions[selected_id[i]]['count'])
        selected_aver.append(functions[selected_id[i]]['aver'])
    with open('invocations_per_function_md.anon.d07.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for i in range(11):
                if row['HashFunction'] == selected_func[i]:
                    tmp = []
                    for col in range(1, 1441):
                        tmp.append(int(row[str(col)]))
                    selected_invo[i] = tmp
    flag = True
    for i in range(11):
        if selected_invo[i] == None:
            flag = False
    if flag == True and sum(selected_invo[0]) < 100000:
        break

for j in range(1440):
    for i in range(11):
        print(selected_invo[i][j], end = ' ')
    print('')
   
for i in range(11):
    if selected_invo[i] != None:
        print('#{} id:{} function:{} average:{} count:{} invocation:{}'.format(i, selected_id[i], selected_func[i], selected_aver[i], selected_count[i], sum(selected_invo[i])))

