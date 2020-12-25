import docker
import time
import math
import gevent
import action_info
import couchdb
from container import Container
from action_info import ActionInfo
from idle_container_algorithm import idle_status_check
from action_manager import ActionManager
from port_manager import PortManager

repack_clean_interval = 2.000 # repack and clean every 5 seconds
dispatch_interval = 0.005 # 200 qps at most
timer = None
update_rate = 0.65 # the update rate of lambda and mu

dispatch_thread = None
repack_clean_thread = None
all_action = {}

# get action info from config file and do initial job
# config_file is the filename of config file
# port_range is a tuple containing the minimum and maximum available port
# db_url and db_name is the url and name of couchdb database
def init(config_file, port_range, db_url, db_name):
    global dispatch_thread, repack_clean_thread, all_action
    info_list = action_info.parse(config_file)

    client = docker.from_env()
    am = ActionManager()
    pm = PortManager(*port_range)

    db_server = couchdb.Server(db_url)
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)
    
    for info in info_list:
        action = Action(client, db, info, pm, am)
        all_action[info.action_name] = action

    dispatch_thread = gevent.spawn_later(dispatch_interval, dispatch) #, all_action)
    repack_clean_thread = gevent.spawn_later(repack_clean_interval, repack_clean) #, all_action)

    return all_action

def dispatch():
    global dispatch_thread, all_action
    dispatch_thread = gevent.spawn_later(dispatch_interval, dispatch)

    for action in all_action.values():
        action.dispatch_request()

def repack_clean():
    global repack_clean_thread, all_action
    repack_clean_thread = gevent.spawn_later(repack_clean_interval, repack_clean)

    for action in all_action.values():
        action.repack_and_clean()

# stop all the action
# function returns when all requests are done
def end():
    for action in all_action.values():
        action.end()
    gevent.killall([dispatch_thread, repack_clean_thread])

class RequestInfo:
    def __init__(self, request_id, data):
        self.request_id = request_id
        self.data = data
        self.result = gevent.event.AsyncResult()
        self.arrival = time.time()

class Action:
    def __init__(self, client, database, action_info, port_manager, action_manager):
        self.client = client
        self.info = action_info
        self.name = action_info.action_name
        self.port_manager = port_manager
        self.action_manager = action_manager
        # self.pwd = pwd
        self.img_name = action_info.img_name
        self.pack_img_name = name + '_repack'
        self.database = database
        self.max_container = action_info.max_container
        
        self.num_processing = 0
        self.rq = []

        # container pool
        self.num_exec = 0
        self.exec_pool = []
        self.lender_pool = []
        self.renter_pool = []

        # start a timer for repack and clean
        # self.repack_clean = gevent.spawn_later(repack_clean_interval, self.repack_and_clean)
        # self.dispatch = gevent.spawn_later(dispatch_interval, self.dispatch_request)
        self.working = set()

        # statistical infomation for idle container identifying
        self.last_request_time = -1
        self.lambd = -1
        self.rec_mu = -1
        self.qos_real = 1
        self.qos_time = action_info.qos_time
        self.qos_requirement = action_info.qos_requirement
        self.request_log = {
            'start': [time.time()],
            'duration': [],
            'alltime': []
        }
    
    # put the request into request queue
    def send_request(self, request_id, data):
        self.working.add(gevent.getcurrent())
        start = time.time()
        self.request_log['start'].append(start)
        self.last_request_time = start
        
        req = RequestInfo(request_id, data)
        req.queue_len = len(self.rq)
        self.rq.append(req)
        res = req.result.get()
        self.database[request_id] = res

        end = time.time()
        self.request_log['duration'].append(res['duration'])
        self.request_log['alltime'].append(end - start)
        self.working.remove(gevent.getcurrent())

    # receive a request from upper layer
    # the precedence of container source:
    #   1. action's executant pool
    #   2. action's renter pool
    #   3. action's lender pool
    #   4. other actions' lender container
    #   5. create new container
    def dispatch_request(self):
        # self.dispatch = gevent.spawn_later(dispatch_interval, self.dispatch_request)

        # no request to dispatch
        if len(self.rq) - self.num_processing == 0:
            return
        self.num_processing += 1

        process_start = time.time()

        # 1.1 try to get a workable container from pool
        container = self.self_container()

        start_way = 'warm'

        # 1.2 try to get a renter container from interaction controller
        rent_start = time.time()
        if container is None:
            container = self.rent_container()
        rent_end = time.time()
        
        # 1.3 create a new container
        create_start = time.time()
        if container is None:
            start_way = 'cold'
            container = self.create_container()
        create_end = time.time()

        # the number of exec container hits limit
        if container is None:
            self.num_processing -= 1
            return

        req = self.rq.pop(0)
        self.num_processing -= 1
        # 2. send request to the container
                
        res = container.send_request(req.data)
        res['start_way'] = start_way
        res['action_name'] = self.name
        res['queue_len'] = req.queue_len
        res['queue_time'] = process_start - req.arrival
        res['rent_time'] = rent_end - rent_start
        res['create_time'] = create_end - create_start
        req.result.set(res)
        
        # 3. put the container back into pool
        self.put_container(container)

    # get a container from container pool
    # if there's no container in pool, return None
    def self_container(self):
        res = None

        if len(self.exec_pool) != 0:
            res = self.exec_pool.pop(-1)
        elif len(self.renter_pool) != 0:
            res = self.renter_pool.pop(-1)
        elif len(self.lender_pool) != 0:
            res = self.lender_pool.pop(-1)
        
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
        
        try:
            container = Container.create(self.client, self.img_name, self.port_manager.get(), 'exec')
        except Exception:
            return None

        self.num_exec += 1
        self.init_container(container)
        return container

    def create_container_with_repacked_image(self):
        print('create_container_with_repacked_image')
        try:
            container = Container.create(self.client, self.pack_img_name, self.port_manager.get(), 'lender')
        except Exception as e:
            print('create error:', e)
            return None

        self.init_container(container)
        self.put_container(container)
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
        return container

    # give out a lender container to interaction controller
    # if there's no lender container, return None
    def giveout_container(self):
        # no container in lender pool
        if len(self.lender_pool) == 0:
            return None

        # take the least hot lender container
        container = self.lender_pool.pop(0)

        gevent.spawn_later(1, self.create_container_with_repacked_image)

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
            "name": self.name,
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
        container.init(self.name)

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

            print("qos: ", new_qos_real, " ", update_rate, " ", sum([x < self.qos_time for x in alltime]), " ", len(alltime), " ", )
            self.qos_real = update_rate * self.qos_real + (1 - update_rate) * new_qos_real

    # do the repack and cleaning work regularly
    def repack_and_clean(self):
        # self.repack_clean = gevent.spawn_later(repack_clean_interval, self.repack_and_clean)

        # find the old containers
        old_container = []
        self.exec_pool = clean_pool(self.exec_pool, exec_lifetime, old_container)
        self.num_exec -= len(old_container)
        self.lender_pool = clean_pool(self.lender_pool, lender_lifetime, old_container)
        self.renter_pool = clean_pool(self.renter_pool, renter_lifetime, old_container)

        # repack containers
        self.update_statistics()
        repack_container = None
        if len(self.exec_pool) > 0:
            n = len(self.exec_pool) + len(self.lender_pool) + len(self.renter_pool)
            idle_sign = idle_status_check(1/self.lambd, n-1, 1/self.rec_mu, self.qos_time, self.qos_real, self.qos_requirement, self.last_request_time)
            print("#idle: ", idle_sign, " ", 1/self.lambd, " ", n-1, " ", 1/self.rec_mu, " ", self.qos_time, " ", self.qos_real, " ", self.qos_requirement, self.last_request_time)
            if idle_sign:
                self.num_exec -= 1
                repack_container = self.exec_pool.pop(0)

        # time consuming work is put here
        for c in old_container:
            self.remove_container(c)
        if repack_container is not None:
            repack_container = self.repack_container(repack_container)
            self.lender_pool.append(repack_container)
            
        if len(self.lender_pool) == 1:
            self.action_manager.have_lender(self.name)
        elif len(self.lender_pool) == 0:
            self.action_manager.no_lender(self.name)
    
    
    # end action's life
    def end(self):
        # gevent.killall([self.repack_clean, self.dispatch])
        gevent.wait(self.working)
        for c in self.exec_pool + self.lender_pool + self.renter_pool:
            self.remove_container(c)

def favg(a):
    return math.fsum(a) / len(a)

# life time of three different kinds of containers
exec_lifetime = 15
lender_lifetime = 30
renter_lifetime = 10

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
