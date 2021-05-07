import os
import signal
import time
from multiprocessing import Process
import subprocess

for i in [30]:
    dir = '/root/sosp/expr/1'
    dir_ = dir + '_openwhisk_24_' + str(i)
    os.system('mkdir ' + dir_)
    os.system('cp ' + dir + '/action_config.yaml ' + '../intraaction_controller/action_config.yaml')
    os.system('python3 ../interaction_controller/test_inter/init.py')
    inter = subprocess.Popen(['python3', '../interaction_controller/inter_controller.py'])
    time.sleep(10)
    intra = subprocess.Popen(['python3', '../intraaction_controller/proxy.py', str(5001), str(1), str(i)])
    time.sleep(10)
    overhead = subprocess.Popen(['python3', 'overhead.py', str(inter.pid), str(intra.pid)])
    os.system('python3 send_request.py ' + dir + '/set.json')
    os.system('sudo kill -9 ' + str(overhead.pid))
    os.system('sudo kill -9 ' + str(inter.pid))
    os.system('sudo kill -9 ' + str(intra.pid))
    os.system('python3 get_results.py ' + dir_)
    time.sleep(5) 