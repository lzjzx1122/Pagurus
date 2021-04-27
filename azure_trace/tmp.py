total = 24894
Range_number = 3880
M = total / Range_number
L, R = [], []
for i in range(Range_number):
    L.append(round(i * M))
for i in range(Range_number - 1):
    R.append(L[i + 1] - 1)
R.append(total - 1)

for i in range(Range_number):
    print(L[i], R[i])