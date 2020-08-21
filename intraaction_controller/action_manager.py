import requests
import time
import json

class ActionManager:
    def __init__(self):
        self.url = 'http://172.23.164.203:5000'
    
    def rent(self, action_name):
        try:
            print("send rent: ", action_name)
            res = requests.post(self.url + "/rent", json = {"action_name": action_name})
            if res.text == "no lender":
                return None
            else:
                res_dict = json.loads(res.text)
                return res_dict['id'], res_dict['port']
        except Exception:
            return None  

    def create_pack_image(self, action_name):
        while True:
            try:
                print("send create_pack_image: ", action_name)
                res = requests.post(self.url + "/repack_image", json = {"action_name": action_name})
                return res.text
                break
            except Exception:
                time.sleep(0.01)

    def have_lender(self, action_name):
        print("send have_lender: ", action_name)
        while True:
            try:
                res = requests.post(self.url + "/have_lender", json = {"action_name": action_name})
                break
            except Exception:
                time.sleep(0.01)

    def no_lender(self, action_name):
        print("send no_lender: ", action_name)
        while True:
            try:
                res = requests.post(self.url + "/no_lender", json = {"action_name": action_name})
                break
            except Exception:
                time.sleep(0.01)
