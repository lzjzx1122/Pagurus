import os 

for i in range(1, 19):
    os.system('python3 summary.py ' + 'expected_result/' + str(i))