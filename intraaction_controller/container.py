import requests
import docker
import time
from gevent import queue
import gevent

base_url = 'http://127.0.0.1:{}/{}'

class Container:
    # create a new container and return the wrapper
    @classmethod
    def create(cls, client, image_name, port, attr):
        container = client.containers.run(image_name, detach=True, ports={'5000/tcp': str(port)})
        res = cls(container, port, attr)

        while res.get_status() != 'new':
            gevent.sleep(0.005)

        return res

    # get the wrapper of an existed container
    # container_id is the container's docker id
    @classmethod
    def inherit(cls, client, container_id, port, attr):
        container = client.containers.get(container_id)
        return cls(container, port, attr)

    def __init__(self, container, port, attr):
        self.container = container
        self.port = port
        self.attr = attr
        self.lasttime = time.time()
        self.run = False
        self.runner = None

    # continously get request from queue
    def request_loop(self, rq):
        self.run = True
        self.runner = gevent.spawn(self._request_loop, rq)

    # stop the request pulling loop
    def stop_loop(self):
        self.run = False
        self.runner.join()
        # gevent.wait(self.runner)

    def _request_loop(self, rq):
        while self.run:
            try:
                request = rq.get(timeout=0.05)
            except queue.Empty:
                continue

            res = self.send_request(request.data)
            request.result.set(res)

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
        self.lasttime = time.time()
        return r.json()

    # initialize the container
    def init(self, action_name, pwd):
        data = { 'action': action_name, 'pwd': pwd}
        r = requests.post(base_url.format(self.port, 'init'), json=data)

        self.lasttime = time.time()
        return r.status_code == 200

    # kill and remove the container
    def destroy(self):
        self.container.remove(force=True)
