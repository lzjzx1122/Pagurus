import os
import sys
import time
import requests
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from multiprocessing import Process

base_url = 'http://127.0.0.1:{}/{}'
exec_path = '/proxy/exec/'
default_file = 'main.py'

class ActionRunner:
    def __init__(self):
        self.code = None
        self.action = None
        self.action_context = None

    def init(self, inp):
        action = inp['action']

        # update action status
        self.action = action

        # delete other packages
        if os.path.isfile('/venv'):
            os.system('rm -r /venv/!("{}")'.format(self.action))
        # add python_path
        if not sys.path.count('/venv/{}'.format(self.action)):
            sys.path.append('/venv/{}'.format(self.action))
        # compile the python file first
        filename = os.path.join(exec_path, action + '/' + default_file)
        with open(filename, 'r') as f:
            code = compile(f.read(), filename, mode='exec')

        self.action_context = {}
        exec(code, self.action_context)

        return True

    def run(self, inp):
        # insert the input to action's context
        self.action_context['data'] = inp

        # run the action
        out = eval('main(data)', self.action_context)
        return out

proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
runner = ActionRunner()

@proxy.route('/status', methods=['GET'])
def status():
    res = {}
    res['status'] = proxy.status
    res['workdir'] = os.getcwd()
    if runner.action:
        res['action'] = runner.action
    return res

@proxy.route('/init', methods=['POST'])
def init():
    proxy.status = 'init'

    inp = request.get_json(force=True, silent=True)
    runner.action = inp['action']
    st = time.time()
    os.system('su -c "python3 sub_proxy.py" {}'.format(runner.action))
    ed = time.time()
    r = requests.post(base_url.format(4999, 'init'), json=inp)
    # runner.init(inp)

    proxy.status = 'ok'
    return {
        "duration": ed - st
    }

@proxy.route('/run', methods=['POST'])
def run():
    proxy.status = 'run'
    
    inp = request.get_json(force=True, silent=True)
    # record the execution time
    start = time.time()

    r = requests.post(base_url.format(4999, 'run'), json=inp)
    # runner.run(inp)
    '''
    process_ = Process(target=runner.run, args=[inp])
    process_.start()
    process_.join(timeout=max(0, inp['timeout'] - 0.005))
    process_.terminate()
    '''

    # out = runner.run(inp)
    end = time.time()
    print('duration:', end - start)
    data = {
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        # "result": out
    }

    proxy.status = 'ok'
    return data

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    server.serve_forever()
