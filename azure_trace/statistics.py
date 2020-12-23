import csv
import numpy as np

average = []
count = []
minimum = []
maximum = []

cnt = 0
with open('function_durations_percentiles.anon.d01.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        average.append(int(row['Average']))
        count.append(int(row['Count']))
        minimum.append(int(row['Minimum']))
        maximum.append(int(row['Maximum']))
        interval = 24 * 60 / int(row['Count'])
        if interval < 15:
            print(interval, int(row['Count']))
            cnt += 1
        # print(int(row['Average']), interval)
        # if int(row['Average']) > interval:
        #    cnt += 1
        
print('cnt:', cnt)

print('total_line:', len(average))
M = len(average) / 11
L, R = [], []
for i in range(11):
    L.append(round(i * M))
for i in range(10):
    R.append(L[i + 1] - 1)
R.append(len(average) - 1)
# print(L)
# print(R)
# print(average)
'''
for i in range(11):
    l, r = L[i], R[i]
    mid = (l + r) // 2
    count_mid = count[mid]
    average_average = np.mean(average[l: r + 1])
    # print(np.mean(count[l: r + 1]))
    # print(np.sqrt(np.var(count[l: r + 1])))
    print('For segment [{}, {}], count at middle is {} everyday({} in every minute, {} in every second), average time is {} ms'.format(l, r, count_mid, count_mid / 24 / 60, count_mid / 24 / 60 / 60, average_average))
'''    