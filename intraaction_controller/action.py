import docker
import time
import math
from threading import Lock, Timer
from container import Container
from idle_container_algorithm import idle_status_check

interval = 5 # repack and clean every 5 seconds
timer = None
update_rate = 0.85 # the update rate of lambda and mu

class Action:
    def __init__(self, client, action_name, pwd, port_manager, action_manager, database, qos_time, qos_requirement):
        self.client = client
        self.name = action_name
        self.port_manager = port_manager
        self.action_manager = action_manager
        self.pwd = pwd
        self.img_name = 'action_' + action_name
        self.pack_img_name = None
        self.database = database

        # any modification of pool should first acquire pool's lock
        self.pool_lock = Lock()
        self.exec_pool = []
        self.lender_pool = []
        self.renter_pool = []

        # start a timer for repack and clean
        global timer
        timer = Timer(interval, repack_and_clean, args=[self])
        timer.start()

        # statistical infomation for idle container identifying
        self.lambd = -1
        self.rec_mu = -1
        self.qos_real = 0
        self.qos_time = qos_time
        self.qos_requirement = qos_requirement
        self.request_log = []

    # receive a request from upper layer
    # the precedence of container source:
    #   1. action's executant pool
    #   2. action's renter pool
    #   3. action's lender pool
    #   4. other actions' lender container
    #   5. create new container
    def send_request(self, request_id, data):
        # TODO: have big problem, will create too many containers
        start = time.time()

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
        self.database[request_id] = res

        # update statistical infomation for idle
        end = time.time()
        self.request_log.append((start, end))

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
            self.pack_img_name = self.action_manager.create_pack_image(self.name)
        
        container = Container.create(self.client, self.pack_img_name, container.port, 'lender')
        self.init_container(container)
        return container

    # give out a lender container to interaction controller
    # if there's no lender container, return None
    def giveout_container(self):
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

    # after the destruction of container
    # its port should be give back to port manager
    def remove_container(self, container):
        container.destroy()
        self.port_manager.put(container.port)
    
    # return the status of all container pools
    def pool_status(self):
        return {
            "exec": len(self.exec_pool),
            "lender": len(self.lender_pool),
            "renter": len(self.renter_pool),
            "lambda": self.lambd,
            "rec_mu": self.rec_mu,
            "qos_real": self.qos_real
        }

    # remove all lender containers in lender pool
    # it should be called when pack image (lender's image) has been changed
    def remove_lender(self):
        self.pool_lock.acquire()
        lenders = self.lender_pool
        self.lender_pool = []
        self.pool_lock.release()

        for c in lenders:
            self.remove_container(c)

    # do the action specific initialization work
    def init_container(self, container):
        container.init(self.name, self.pwd)

    def update_statistics(self):
        # do not update if no requests, or only one came
        if len(self.request_log) < 2:
            return

        logs = self.request_log
        self.request_log = []
        # sort all logs by start time
        logs.sort(key=lambda x: x[0])

        intervals = [y[0] - x[0] for x, y in zip(logs, logs[1:])]
        new_lambd = favg(intervals)
        durations = [e - s for s, e in logs]
        new_rec_mu = favg(durations)

        self.qos_real = sum([x < self.qos_time for x in durations]) / len(durations)
        if self.lambd > 0:
            self.lambd = update_rate * self.lambd + (1 - update_rate) * new_lambd
        else:
            self.lambd = new_lambd
        if self.rec_mu > 0:
            self.rec_mu = update_rate * self.rec_mu + (1 - update_rate) * new_rec_mu
        else:
            self.rec_mu = new_rec_mu

def favg(a):
    return math.fsum(a) / len(a)

# life time of three different kinds of containers
exec_lifetime = 60
lender_lifetime = 120
renter_lifetime = 40

# do the repack and cleaning work regularly
def repack_and_clean(action):
    # find the old containers
    old_container = []
    action.pool_lock.acquire()
    action.exec_pool = clean_pool(action.exec_pool, exec_lifetime, old_container)
    action.lender_pool = clean_pool(action.lender_pool, lender_lifetime, old_container)
    action.renter_pool = clean_pool(action.renter_pool, renter_lifetime, old_container)
    action.pool_lock.release()

    # repack containers
    action.update_statistics()
    repack_container = None
    action.pool_lock.acquire()
    if len(action.exec_pool) > 0:
        n = len(action.exec_pool) + len(action.lender_pool) + len(action.renter_pool)
        idle_sign = idle_status_check(action.lambd, n, 1/action.rec_mu, action.qos_time, action.qos_real, action.qos_requirement)
        if idle_sign:
            repack_container = action.exec_pool.pop(0)
    action.pool_lock.release()

    # time consuming work is put here
    for c in old_container:
        action.remove_container(c)
    if repack_container is not None:
        repack_container = action.repack_container(repack_container)
        action.pool_lock.acquire()
        action.lender_pool.append(repack_container)
        action.pool_lock.release()

    global timer
    timer = Timer(interval, repack_and_clean, args=[action])
    timer.start()

# the pool list is in order:
# - at the tail is the hottest containers (most recently used)
# - at the head is the coldest containers (least recently used)
def clean_pool(pool, lifetime, old_container):
    cur_time = time.time()
    idx = -1
    for i, c in enumerate(pool):
        print(c.container.short_id, cur_time - c.lasttime)
        if cur_time - c.lasttime < lifetime:
            idx = i
            break
    # all containers in pool are old
    if idx < 0:
        idx = len(pool)
    old_container.extend(pool[:idx])
    return pool[idx:]
