import docker
import time
import math
import gevent
from container import Container
from idle_container_algorithm import idle_status_check

repack_clean_interval = 5.000 # repack and clean every 5 seconds
dispatch_interval = 0.100
timer = None
update_rate = 0.65 # the update rate of lambda and mu

class RequestInfo:
    def __init__(self, request_id, data):
        self.request_id = request_id
        self.data = data
        self.result = gevent.event.AsyncResult()

class Action:
    def __init__(self, client, action_name, pwd, port_manager, action_manager, database, qos_time, qos_requirement, max_container):
        self.client = client
        self.name = action_name
        self.port_manager = port_manager
        self.action_manager = action_manager
        self.pwd = pwd
        self.img_name = 'action_' + action_name
        self.pack_img_name = None
        self.database = database
        self.max_container = max_container
        
        self.num_processing = 0
        self.rq = []

        # container pool
        self.num_exec = 0
        self.exec_pool = []
        self.lender_pool = []
        self.renter_pool = []

        # start a timer for repack and clean
        gevent.spawn_later(repack_clean_interval, repack_and_clean, self)
        gevent.spawn_later(dispatch_interval, self.dispatch_request)

        # statistical infomation for idle container identifying
        self.lambd = -1
        self.rec_mu = -1
        self.qos_real = 1
        self.qos_time = qos_time
        self.qos_requirement = qos_requirement
        self.request_log = {
            'start': [time.time()],
            'duration': [],
            'alltime': []
        }
    
    # put the request into request queue
    def send_request(self, request_id, data):
        start = time.time()
        self.request_log['start'].append(start)

        req = RequestInfo(request_id, data)
        self.rq.append(req)
        res = req.result.get()
        self.database[request_id] = res

        end = time.time()
        self.request_log['duration'].append(res['duration'])
        self.request_log['alltime'].append(end - start)

    # receive a request from upper layer
    # the precedence of container source:
    #   1. action's executant pool
    #   2. action's renter pool
    #   3. action's lender pool
    #   4. other actions' lender container
    #   5. create new container
    def dispatch_request(self):
        gevent.spawn_later(dispatch_interval, self.dispatch_request)

        # no request to dispatch
        print(len(self.rq), self.num_processing)
        if len(self.rq) - self.num_processing == 0:
            return
        self.num_processing += 1

        # 1.1 try to get a workable container from pool
        container = self.self_container()
        # 1.2 try to get a renter container from interaction controller
        if container is None:
            container = self.rent_container()
        # 1.3 create a new container
        if container is None:
            container = self.create_container()
        # the number of exec container hits limit
        if container is None:
            self.num_processing -= 1
            return

        req = self.rq.pop(0)
        self.num_processing -= 1
        # 2. send request to the container
        res = container.send_request(req.data)
        req.result.set(res)
        # 3. put the container back into pool
        self.put_container(container)

    # get a container from container pool
    # if there's no container in pool, return None
    def self_container(self):
        res = None

        if len(self.exec_pool) != 0:
            res = self.exec_pool.pop(0)
        elif len(self.renter_pool) != 0:
            res = self.renter_pool.pop(0)
        elif len(self.lender_pool) != 0:
            res = self.lender_pool.pop(0)
        
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
        # self.put_container(container)
        # return True
        return container

    # create a new container
    def create_container(self):
        # do not create new exec container
        # when the number of execs hits the limit
        if self.num_exec > self.max_container:
            return None
        
        self.num_exec += 1
        container = Container.create(self.client, self.img_name, self.port_manager.get(), 'exec')
        self.init_container(container)
        # self.put_container(container)
        # return True
        return container

    # put the container into one of the three pool, according to its attribute
    def put_container(self, container):
        if container.attr == 'exec':
            self.exec_pool.append(container)
        elif container.attr == 'renter':
            self.renter_pool.append(container)
        elif container.attr == 'lender':
            self.lender_pool.append(container)

    # repack a executant container into a lender container
    # executant container's port will be reused
    def repack_container(self, container):
        container.destroy()

        if self.pack_img_name is None:
            self.pack_img_name = self.action_manager.create_pack_image(self.name)
        
        container = Container.create(self.client, self.pack_img_name, container.port, 'lender')
        self.init_container(container)
        # self.put_container(container)
        # return True
        return container

    # give out a lender container to interaction controller
    # if there's no lender container, return None
    def giveout_container(self):
        # no container in lender pool
        if len(self.lender_pool) == 0:
            return None

        # take the least hot lender container
        container = self.lender_pool.pop(0)

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
            "exec": [self.num_exec, len(self.exec_pool)],
            "lender": len(self.lender_pool),
            "renter": len(self.renter_pool),
            "lambda": self.lambd,
            "rec_mu": self.rec_mu,
            "qos_real": self.qos_real
        }

    # remove all lender containers in lender pool
    # it should be called when pack image (lender's image) has been changed
    def remove_lender(self):
        lenders = self.lender_pool
        self.lender_pool = []

        for c in lenders:
            self.remove_container(c)

    # do the action specific initialization work
    def init_container(self, container):
        container.init(self.name, self.pwd)

    # update stat info for idle alg
    def update_statistics(self):
        if len(self.request_log['start']) > 1:
            logs = self.request_log['start']
            self.request_log['start'] = logs[-1:]
            intervals = [y - x for x, y in zip(logs, logs[1:])]
            new_lambd = favg(intervals)
            if self.lambd > 0:
                self.lambd = update_rate * self.lambd + (1 - update_rate) * new_lambd
            else:
                self.lambd = new_lambd

        if len(self.request_log['duration']) > 0:
            new_rec_mu = favg(self.request_log['duration'])
            self.request_log['duration'] = []
            if self.rec_mu > 0:
                self.rec_mu = update_rate * self.rec_mu + (1 - update_rate) * new_rec_mu
            else:
                self.rec_mu = new_rec_mu

        if len(self.request_log['alltime']) > 0:
            alltime = self.request_log['alltime']
            self.request_log['alltime'] = []
            new_qos_real = sum([x < self.qos_time for x in alltime]) / len(alltime)
            self.qos_real = update_rate * self.qos_real + (1 - update_rate) * new_qos_real

def favg(a):
    return math.fsum(a) / len(a)

# life time of three different kinds of containers
exec_lifetime = 60
lender_lifetime = 120
renter_lifetime = 40

# do the repack and cleaning work regularly
def repack_and_clean(action: Action):
    gevent.spawn_later(repack_clean_interval, repack_and_clean, action)

    # find the old containers
    old_container = []
    action.exec_pool = clean_pool(action.exec_pool, exec_lifetime, old_container)
    action.num_exec -= len(old_container)
    action.lender_pool = clean_pool(action.lender_pool, lender_lifetime, old_container)
    action.renter_pool = clean_pool(action.renter_pool, renter_lifetime, old_container)

    # repack containers
    action.update_statistics()
    repack_container = None
    if len(action.exec_pool) > 0:
        n = len(action.exec_pool) + len(action.lender_pool) + len(action.renter_pool)
        idle_sign = idle_status_check(action.lambd, n-1, 1/action.rec_mu, action.qos_time, action.qos_real, action.qos_requirement)
        if idle_sign:
            action.num_exec -= 1
            repack_container = action.exec_pool.pop(0)

    # time consuming work is put here
    for c in old_container:
        action.remove_container(c)
    if repack_container is not None:
        action.repack_container(repack_container)
        action.lender_pool.append(repack_container)

# the pool list is in order:
# - at the tail is the hottest containers (most recently used)
# - at the head is the coldest containers (least recently used)
def clean_pool(pool, lifetime, old_container):
    cur_time = time.time()
    idx = -1
    for i, c in enumerate(pool):
        if cur_time - c.lasttime < lifetime:
            idx = i
            break
    # all containers in pool are old, or the pool is empty
    if idx < 0:
        idx = len(pool)
    old_container.extend(pool[:idx])
    return pool[idx:]
