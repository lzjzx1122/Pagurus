import json
import os
import yaml
import numpy as np
import random

def random_low():
    lambd = 10 ** (random.randrange(-3000, -2650) / 1000)
    return lambd
    #, list(np.random.poisson(round(lambd, 3), 00))

def random_mid():
    lambd = 10 ** (random.randrange(-2000, 0) / 1000)
    return lambd
    #, list(np.random.poisson(round(lambd, 3), 3600))

def random_high():
    lambd = 10 ** (random.randrange(300, 600) / 1000)
    return lambd
    #, list(np.random.poisson(round(lambd, 3), 3600))


wf = json.loads(open('wfs.json', encoding='utf-8').read())
for app in wf:
    for func in wf[app]:
        wf[app][func]['duration'] /= 2
        wf[app][func]['start_time'] /= 2

for i in range(9, 11):
    
    lambd = []
    for _ in range(2):
        lambd.append(random_low())
    for _ in range(6):
        lambd.append(random_mid())
    for _ in range(2):
        lambd.append(random_high())
    random.shuffle(lambd)
    print(lambd)

    os.system('mkdir new_trace/' + str(i))
    trace = {}
    cnt = 0
    for app in wf:
        l = lambd[cnt]
        cnt += 1
        invo_ = list(np.random.poisson(round(l, 3), 7200))
        invo = []
        for _ in invo_:
            invo.append(int(_))
        trace[app] = {'lambda': l, 'invo': invo, 'functions': wf[app]}

    f = open('new_trace/' + str(i) + '/trace.json', 'w', encoding = 'utf-8')
    json.dump(trace, f, sort_keys = False, indent = 4)