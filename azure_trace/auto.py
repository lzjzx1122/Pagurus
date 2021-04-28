import os
import signal
import time
from multiprocessing import Process
import subprocess

for i in range(1, 2):
    dir = '/root/sosp/expr/' + str(i)
    dir_ = dir + '_openwhisk'
    os.system('mkdir ' + dir_)
    os.system('cp ' + dir + '/action_config.yaml ' + '../intraaction_controller/action_config.yaml')
    os.system('python3 ../interaction_controller/test_inter/init.py')
    inter = subprocess.Popen(['python3', '../interaction_controller/inter_controller.py'])
    time.sleep(10)
    intra = subprocess.Popen(['python3', '../intraaction_controller/proxy.py', str(5001)])
    time.sleep(10)
    overhead = subprocess.Popen(['python3', 'overhead.py', str(inter.pid), str(intra.pid)])
    os.system('python3 send_request.py ' + dir + '/set.json')
    os.system('sudo kill -9 ' + str(overhead.pid))
    os.system('sudo kill -9 ' + str(inter.pid))
    os.system('sudo kill -9 ' + str(intra.pid))
    os.system('python3 get_results.py ' + dir_)
    time.sleep(5)