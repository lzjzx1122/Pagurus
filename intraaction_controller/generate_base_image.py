import json
import os

os.system('docker build --no-cache -t pagurus_base ../container')
os.system('docker build --no-cache -t pagurus_prewarm_base ../prewarm_container')
data = json.load(open('./build_file/packages.json', 'r'))
for function in data:
    os.system('docker build --no-cache -t action_' + function + ' ./images_save/' + function)
