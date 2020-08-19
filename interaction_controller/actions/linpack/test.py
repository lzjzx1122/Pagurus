import subprocess
import time

for _ in range(10):
    subprocess.Popen(['python3', 'main.py'])

time.sleep(20)
