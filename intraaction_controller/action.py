import docker
from threading import Lock, Timer
from container import Container

interval = 5 # repack and clean every 5 seconds
timer = None

class Action:
    def __init__(self, client, action_name, pwd, port_manager, action_manager):
        self.client = client
        self.name = action_name
        self.port_manager = port_manager
        self.action_manager = action_manager
        self.pwd = pwd
        self.img_name = 'img_' + action_name
        self.pack_img_name = None

        # any modification of pool should first acquire pool's lock
        self.pool_lock = Lock()
        self.exec_pool = []
        self.lender_pool = []
        self.renter_pool = []

        # start a timer for repack and clean
        global timer
        timer = Timer(interval, repack_and_clean, args=[self])

    # receive a request from upper layer
    # the precedence of container source:
    #   1. action's executant pool
    #   2. action's renter pool
    #   3. action's lender pool
    #   4. other actions' lender container
    #   5. create new container
    def send_request(self, data):
        # 1.1 try to get a workable container from pool
        container = self.self_container()
        # 1.2 try to get a renter container from interaction controller
        if container is None:
            container = self.rent_container()
        # 1.3 create a new container
        if container is None:
            container = self.create_container()

        # 2. send request to the container
        res = container.send_request(data)
        # 3. put the container back into pool
        self.put_container(container)

        # 4. write the result into database
        # TODO: write the result into couchdb

    # get a container from container pool
    # if there's no container in pool, return None
    def self_container(self):
        res = None

        self.pool_lock.acquire()
        if len(self.exec_pool) != 0:
            res = self.exec_pool.pop(-1)
        elif len(self.renter_pool) != 0:
            res = self.renter_pool.pop(-1)
        elif len(self.lender_pool) != 0:
            res = self.lender_pool.pop(-1)
        self.pool_lock.release()
        
        return res

    # rent a container from interaction controller
    # if no container can be rented, return None
    def rent_container(self):
        res = self.action_manager.rent(self.name)
        if res is None:
            return None
        
        container_id, port = res
        container = Container.inherit(self.client, container_id, port, 'renter')
        self.init_container(container)
        return container

    # create a new container
    def create_container(self):
        container = Container.create(self.client, self.img_name, self.port_manager.get(), 'exec')
        self.init_container(container)
        return container

    # put the container into one of the three pool, according to its attribute
    def put_container(self, container):
        self.pool_lock.acquire()
        if container.attr == 'exec':
            self.exec_pool.append(container)
        elif container.attr == 'renter':
            self.renter_pool.append(container)
        elif container.attr == 'lender':
            self.lender_pool.append(container)
        self.pool_lock.release()

    # repack a executant container into a lender container
    # executant container's port will be reused
    def repack_container(self, container):
        container.destroy()

        if self.pack_img_name is None:
            self.action_manager.create_pack_image()
        
        container = Container.create(self.client, self.pack_img_name, container.port, 'lender')
        self.init_container(container)
        return container

    # give out a lender container to interaction controller
    # if there's no lender container, return None
    def giveout_container(self, container):
        self.pool_lock.acquire()
        # no container in lender pool
        if len(self.lender_pool) == 0:
            self.pool_lock.release()
            return None

        # take the least hot lender container
        container = self.lender_pool.pop(0)
        self.pool_lock.release()

        container_id = container.container.id
        port = container.port
        return container_id, port
    
    # return the status of all container pools
    def pool_status(self):
        return {
            "exec": len(self.exec_pool),
            "lender": len(self.lender_pool),
            "renter": len(self.renter_pool)
        }

    # remove all lender containers in lender pool
    # it should be called when pack image (lender's image) has been changed
    def remove_lender(self):
        self.pool_lock.acquire()
        lenders = self.lender_pool
        self.lender_pool = []
        self.pool_lock.release()

        for c in lenders:
            c.destroy()

    # do the action specific initialization work
    def init_container(self, container):
        container.init(self.name, self.pwd)

def repack_and_clean(action):
    # TODO: repack and clean

    global timer
    timer = Timer(interval, repack_and_clean, args=[action])


# intra-action 接口
# 1. 接受inter的repack消息, 需要销毁所有的lender容器
# ps. container repack的时机由intra选择
# 全局定时器定时检查可以repack的container和可以销毁的container
# 2. 接受action run的请求
# 3. 取走lender container
# 4. 每种状态的容器的数量
