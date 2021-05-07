import json
import os
import yaml

def gen_func(name):
    os.system('mkdir aws_actions/' + name)
    os.system('cp main.py aws_actions/' + name)

cnt = 0
wf = json.loads(open('wfs.json', encoding='utf-8').read())
packages = {}
actions_config = []
for app in wf:
    for func in wf[app]:
        actions_config.append({'name': func, 'image': 'action_' + func, 'qos_time': 1, 'qos_requirement': 0.95})
        # gen_func(func)
        # print(app, func)
        cnt += 1
        tmp = wf[app][func]['packages']
        res = {}
        for pkg in tmp:
            res[pkg] = tmp[pkg]['version']
        packages[func] = res
   
action_config = {'max_container': 10, 'actions': actions_config}
f = open('action_config.yaml', 'w', encoding = 'utf-8')
yaml.dump(action_config, f)

print(cnt)
f = open('aws_packages.json', 'w', encoding = 'utf-8')
json.dump(packages, f, sort_keys = False, indent = 4)