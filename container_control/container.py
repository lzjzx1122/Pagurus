import requests
import docker
import time

base_url = 'http://127.0.0.1:{}/{}'

class Container:
    # create and initialize a container
    def __init__(self, client, image_name, port, action_name, pwd):
        self.container = client.containers.run(image_name, detach=True, ports={'5000/tcp': str(port)})
        self.port = port
        
        while self.get_status() != 'new':
            time.sleep(0.005)

        self.init(action_name, pwd)

    # get the status of container
    # start: the proxy server does not work
    # new: the server works, but not init
    # init: in the process of init
    # ok: ready to handle request
    # run: in the process of handling request
    def get_status(self):
        try:
            r = requests.get(base_url.format(self.port, 'status'))
            return r.json()['status']
        except Exception:
            return 'start'

    # send a request to container and wait for result
    def send_request(self, data = {}):
        r = requests.post(base_url.format(self.port, 'run'), json=data)
        return r.json()

    # initialize the container
    def init(self, action_name, pwd):
        data = { 'action': action_name, 'pwd': pwd}
        r = requests.post(base_url.format(self.port, 'init'), json=data)
        return r.status_code == 200

    # kill and remove the container
    def destroy(self):
        self.container.remove(force=True)