import os
import signal
import time
from multiprocessing import Process
import subprocess
import sys


# option = sys.argv[1]


# for i in [2, 3, 4, 5]:
#     for option in ['prewarm', 'sock', 'openwhisk', 'pagurus']:

for i in [2]:
    for option in ['pagurus']:
        dir = '/root/Pagurus/aws/result/' + str(i)
        
        option_dir = dir + '/' + option

        if os.path.exists(option_dir):
            os.system('rm -rf ' + option_dir)
        os.system('mkdir ' + option_dir)
    
        os.system('python3 clear_containers.py')
        
        inter = subprocess.Popen(['python3', '../interaction_controller/inter_controller.py', 'experiment'])
        time.sleep(5)

        intra = subprocess.Popen(['python3', '../intraaction_controller/intra_controller.py', str(5001), str(1), str(60), option])
        if option == 'sock':
            time.sleep(120)
        else:
            time.sleep(5)

        os.system('python3 send_requests_.py ' + dir + '/trace.json')
        
        os.system('./kill.sh ' + str(inter.pid))
        os.system('./kill.sh ' + str(intra.pid))

        os.system('python3 get_results.py ' + option_dir)
        time.sleep(5)
