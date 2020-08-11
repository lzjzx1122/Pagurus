import requests
import time

class ActionManager:
    def __init__(self):
        pass
    
    def rent(self, action_name):
        try:
            res = requests.post("http://0.0.0.0:5000/rent", json = {"action_name": action_name})
            if res.text == "NO":
                return None
            else:
                return res.text
        except Exception:
            return None  

    def create_pack_image(self, action_name):
        while True:
            try:
                res = requests.post("http://0.0.0.0:5000/repack_image", json = {"action_name": action_name})
                return res.text
                break
            except Exception:
                time.sleep(0.01)

    def have_lender(self, action_name):
        while True:
            try:
                res = requests.post("http://0.0.0.0:5000/have_lender", json = {"action_name": action_name})
                break
            except Exception:
                time.sleep(0.01)

    def no_lender(self, action_name):
         while True:
            try:
                res = requests.post("http://0.0.0.0:5000/no_lender", json = {"action_name": action_name})
                break
            except Exception:
                time.sleep(0.01)
