import requests
import docker
import time
import gevent
import file_controller
from docker.types import Mount

base_url = 'http://127.0.0.1:{}/{}'
exec_dir = '/proxy/exec'

class Container:
    # create a new container and return the wrapper
    @classmethod
    def create(cls, client, image_name, port, attr):
        path, dir_id = file_controller.create_dir()
        mount = Mount(exec_dir, path, type='bind')
        container = client.containers.run(image_name,
                                          detach=True,
                                          ports={'5000/tcp': str(port)},
                                          labels=['pagurus'],
                                          mounts=[mount])
        file_controller.bind(dir_id, container.id)

        res = cls(container, port, attr)
        res.wait_start()
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

    # wait for the container cold start
    def wait_start(self):
        while True:
            try:
                r = requests.get(base_url.format(self.port, 'status'))
                if r.status_code == 200:
                    break
            except Exception:
                pass
            gevent.sleep(0.005)

    # send a request to container and wait for result
    def send_request(self, data = {}):
        r = requests.post(base_url.format(self.port, 'run'), json=data)
        self.lasttime = time.time()
        return r.json()

    # initialize the container
    def init(self, action_name):
        file_controller.put_file_container(self.container.id, action_name)
        data = { 'action': action_name }
        r = requests.post(base_url.format(self.port, 'init'), json=data)
        self.lasttime = time.time()
        return r.status_code == 200

    # kill and remove the container
    def destroy(self):
        print("################################## destory: ", self.port)
        container_id = self.container.id
        self.container.remove(force=True)
        file_controller.destroy_container_dir(container_id)
