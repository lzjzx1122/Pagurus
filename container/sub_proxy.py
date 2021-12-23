import os
import sys
import time
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from multiprocessing import Process

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

        # add python_path
        if not sys.path.count('/home/{}'.format(self.action)):
            sys.path.append('/home/{}'.format(self.action))
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




@proxy.route('/init', methods=['POST'])
def init():
    inp = request.get_json(force=True, silent=True)
    runner.init(inp)
    return ('OK', 200)


@proxy.route('/run', methods=['POST'])
def run():
    inp = request.get_json(force=True, silent=True)
    runner.run(inp)
    return ('OK', 200)


if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 4999), proxy)
    server.serve_forever()
