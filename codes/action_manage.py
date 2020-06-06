import os
import docker
import time
import asyncio
from multiprocessing import Value,Process,Array
from idle_algorithm.cal import Qos_value_algorithm
#from check_post import action_post
#from load_check import load_check
from status_communication import status_communication
from container_manage import action_container
from threading import Thread

def asynci(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        return wrapper

@asynci
def container_prepare_and_run(container, port_number):
    global post_status
    global current_containers
    global container_time_counting
    global exec_time_list
    global mu

    tmp = current_containers
    current_containers += 1

    if post_status[tmp] == -1:
        post_status[tmp] = 0
        container.create(port_number + tmp)
        container.code_loading(port_number + tmp)
        start = time.time()
        container.run_action(port_number + tmp)
        container_time_counting = time.time()
        post_status[tmp] = 1

        exec_time_list.append(container_time_counting - start)
        if mu == 0:
            mu = 1/(container_time_counting - start)

@asynci
def container_execution(container, port_number, idle_index, type_invoke):
    global post_status
    global current_containers
    global container_time_counting
    global exec_time_list
    global mu
    global lender_count

    start = time.time()
    if type_invoke == 0:
        post_status[idle_index] = 0
        container.run_action(port_number + idle_index)
        if idle_index == current_containers - lender_count - 1:
            container_time_counting = time.time()
        post_status[idle_index] = 1
    elif type_invoke == 1:
        lender_post_status[idle_index] = 0
        container.run_action(port_number + idle_index)
        if idle_index == current_containers - lender_count - 1:
            container_time_counting = time.time()
        lender_post_status[idle_index] = 1

    exec_time_list.append(time.time() - start)

    if len(exec_time_list) == 10:
        mu = len(exec_time_list) / sum(exec_time_list)
        print(mu)
        exec_time_list = [] 

@asynci
def container_delete(container,port_number,max_containers):
    global current_containers
    global post_status
    global container_time_counting
    global lender_count
    global shared_status
    global renter_port_number

    time.sleep(30)
    while current_containers > 0:
        #print(container_time_counting)
        try:
            shared_index = shared_status.index(-1)
            if lender_count == 0:
                raise ValueError
        except ValueError: #or lender_count == 0:
            if time.time() - container_time_counting > 60 and post_status[current_containers - 1] == 1:
                tmp = current_containers - 1
                current_containers -= 1

                container.remove(port_number + tmp)
                print('now container port ',port_number + tmp,'deleted ')

                post_status[tmp] = -1
                
                if current_containers > 0 and post_status[current_containers - 1] == 1:
                    container_time_counting = time.time()
            else:pass

    container_time_counting = time.time()
    while lender_count > 0:
        if time.time() - container_time_counting > 120 and lender_post_status[lender_count - 1] == 1:
            container.lender_remove(renter_port_number + lender_count - 1)
            print('now lender container port ',renter_port_number + lender_count - 1,'deleted ')
            lender_count -= 1
            shared_status[lender_count] = -1
            lender_post_status[lender_count] = -1
            if lender_count > 0 and lender_post_status[lender_count - 1] == 1:
                    container_time_counting = time.time()
        else:pass
        time.sleep(1)

@asynci
def idle_algorithm(container,status_manager,action_speed,container_u,action_Qos_time,action_Qos_value):
    global current_containers
    global mu
    global lender_id
    global lender_count
    global max_lender
    global shared_status
    global renter_port_number

    time.sleep(20)
    print('algorithm running')
    while current_containers > 0:
        lender_id = status_manager.status_check(action_speed, current_containers, mu, action_Qos_time, action_Qos_value)
        if lender_count < max_lender and lender_id > 0:
            tmp = lender_count
            lender_count += 1
            #current_containers += 1
            if lender_post_status[tmp] == -1:
                lender_post_status[tmp] = 0
                container.lender_create(renter_port_number + tmp)
                container.code_loading(renter_port_number + tmp)
                while current_containers > 0:
                    if post_status[current_containers - 1] == 1:
                        tmp_cur_cont = current_containers - 1
                        current_containers -= 1
                        post_status[tmp_cur_cont] = -1
                        container.remove(port_number + tmp_cur_cont)
                        print('now container port ',port_number + tmp_cur_cont,'deleted ')
                        shared_status[tmp] = 1
                        break
                lender_post_status[tmp] = 1
        time.sleep(1)


#status_container = []
post_status = [-1] * max_containers
lender_post_status = [-1] * max_lender
shared_status = [-1] * max_lender
# #post_status = Array('i',max_containers)
# for i in range(max_containers):
#     #post_status[i] = -1
#     post_status.append(-1)
# for i in range(max_lender):
#     #post_status[i] = -1
#     lender_post_status.append(-1)
# for i in range(max_lender):
#     #post_status[i] = -1
#     shared_status.append(-1)


def test():
    for i in range(50):
        try:
            idle_index = post_status.index(1)
        except ValueError:
            try:
                lender_index = lender_post_status.index(1)
            except ValueError:
                if current_containers < max_containers - lender_count:
                    container_prepare_and_run(obj_container,port_number)
                else: pass
            else:
                container_execution(obj_container,renter_port_number,lender_index,1)
        else:
            if idle_index < max_containers:
                container_execution(obj_container,port_number,idle_index,0)
        time.sleep(1/action_speed)


