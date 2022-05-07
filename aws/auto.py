import os
import signal
import time
from multiprocessing import Process
import subprocess
import sys

option = sys.argv[1]

for i in range(1, 2):
    dir = '/users/Linsong/Pagurus/aws/result/' + str(i)
    option_dir = dir + '/' + option

    if os.path.exists(option_dir):
        os.system('rm -rf ' + option_dir)
    os.system('mkdir ' + option_dir)
   
    os.system('sudo python3 clear_containers.py')
    
    inter = subprocess.Popen(['sudo', 'python3', '../interaction_controller/inter_controller.py', 'experiment'])
    print('inter_pid:', inter.pid)
    time.sleep(2)

    intra = subprocess.Popen(['sudo', 'python3', '../intraaction_controller/intra_controller.py', str(5001), str(1), str(60), 'pagurus'])
    time.sleep(1)
    
    os.system('python3 send_requests_.py ' + dir + '/trace.json')
    
    # os.system('sudo kill -9 ' + str(inter.pid))
    # os.system('sudo kill -9 ' + str(intra.pid))

    os.system('./kill.sh ' + str(inter.pid))
    os.system('./kill.sh ' + str(intra.pid))

    os.system('python3 get_results.py ' + option_dir)
    # time.sleep(5)


# 1620154484.86702
#1620153249.41937