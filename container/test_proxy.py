import os
import sys
import time

st = time.time()
# os.system('su -c "python3 sub_proxy.py" {}'.format(sys.argv[1]))
os.system('ls')
ed = time.time()
print(ed-st)