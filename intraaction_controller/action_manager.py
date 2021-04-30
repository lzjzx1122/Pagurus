import requests
import gevent
import time

class ActionManager:
    def __init__(self):
        self.inter_port = 5000
    
    def rent(self, action_name):
        try:
            res = requests.post('http://0.0.0.0:' + str(self.inter_port) + '/rent', json = {'action_name': action_name})
            if res.text == 'no lender':
                return None
            else:
                res_dict = res.json()
                return res_dict['id'], res_dict['port']
        except Exception:
            return None  

    def create_pack_image(self, action_name):
        while True:
            try:
                # print('send create_pack_image: ', action_name)
                res = requests.post('http://0.0.0.0:' + str(self.inter_port) + '/repack_image', json = {'action_name': action_name})
                return res.text
            except Exception:
                gevent.sleep(0.01)

    def have_lender(self, action_name):
        # print('send have_lender: ', action_name)
        while True:
            try:
                res = requests.post('http://0.0.0.0:'+ str(self.inter_port) +  '/have_lender', json = {'action_name': action_name})
                break
            except Exception:
                gevent.sleep(0.01)

    def no_lender(self, action_name):
        # print('send no_lender: ', action_name)
        while True:
            try:
                res = requests.post('http://0.0.0.0:' + str(self.inter_port) + '/no_lender', json = {'action_name': action_name})
                break
            except Exception:
                gevent.sleep(0.01)

    def cold_start(self, action_name):
        requests.post('http://0.0.0.0:' + str(self.inter_port) + '/cold_start', json = {'action_name': action_name})