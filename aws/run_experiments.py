import os
import signal
import time
from multiprocessing import Process
import subprocess
import sys

result_dir = '/root/Pagurus/aws/result/1/'
trace_dir = '/root/Pagurus/aws/trace/1/'

if os.path.exists(result_dir):
    os.system('rm -rf ' + result_dir)
os.system('mkdir ' + result_dir)

for option in ['prewarm', 'sock', 'pagurus', 'openwhisk']: # ['pagurus', 'openwhisk', 'prewarm', 'sock']:    
    option_dir = result_dir + option

    if os.path.exists(option_dir):
        os.system('rm -rf ' + option_dir)
    os.system('mkdir ' + option_dir)

    os.system('python3 clear_containers.py')
    
    inter = subprocess.Popen(['python3', '../interaction_controller/inter_controller.py', 'aws'])
    time.sleep(5)

    intra = subprocess.Popen(['python3', '../intraaction_controller/intra_controller.py', str(5001), str(1), str(60), option, 'aws'])
    if option == 'sock':
        time.sleep(120)
    else:
        time.sleep(5)

    os.system('python3 send_requests.py ' + trace_dir + 'trace.json')
    
    os.system('./kill.sh ' + str(inter.pid))
    os.system('./kill.sh ' + str(intra.pid))

    os.system('python3 get_results.py ' + option_dir)
    time.sleep(5)

os.system('python3 summary.py ' + result_dir)