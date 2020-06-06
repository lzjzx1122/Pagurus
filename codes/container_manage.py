import os
import docker
import time
import requests
#from threading import Thread

#def asynci(f):
#        def wrapper(*args, **kwargs):
#            thr = Thread(target=f, args=args, kwargs=kwargs)
#            thr.start()
#        return wrapper
class action_info():
    def __init__(self,container,port_number):
        self.container = container
        self.container_id = container.id
        self.port_number = port_number
        self.status = ''
        self.out = ''
        self.packages = {}
        self.dockerfile = {}
        self.start_time = time.time()
    

class action_container():
    def __init__(self,user_path,action_name,pack_img_name,max_containers,lender_count):
        self.client = docker.from_env()
        self.user_path = user_path
        self.action_name = action_name
        self.pack_img_name = pack_img_name
        self.lender_count = 1
        #self.max_containers = max_containers
        #self.current_containers = 0
        self.instance_info = [None for index in range(max_containers)]
        self.renter_instance_info = [None for index in range(lender_count)]
        self.lender_instance_info = [None for index in range(lender_count)]

    def lender_create(self,port_number):
        start_time = time.time()
        temp_container = self.client.containers.run('lzjzx1122/python3action_pack_'+self.pack_img_name,command = 'python3 /actionProxy/apigateway.py',ports = {"18080/tcp":port_number},detach = True,tty = True, stdin_open = True)
        temp_action_info = action_info(temp_container,port_number)
        self.lender_instance_info[port_number-19081] = temp_action_info
        while True:
            try:
                request = requests.get('http://0.0.0.0:' + str(port_number) + '/checkstatus')

                if request.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.01)
        time_passed = time.time() - start_time
        if port_number == 19081:
            print('creating time is ',time_passed)


    def create(self,port_number):
        start_time = time.time()
        temp_container = self.client.containers.run('lzjzx1122/python3action_app_'+self.action_name,command = 'python3 /actionProxy/apigateway.py',ports = {'18080/tcp': port_number},detach = True,stdin_open = True)
        
        #temp_container = self.client.containers.run('pzf/python3action',command = 'python3 /actionProxy/apigateway.py',ports = {'18080/tcp': port_number},detach = True,tty = True,stdin_open = True)

        temp_action_info = action_info(temp_container,port_number)
        self.instance_info[port_number-18081] = temp_action_info

        while True:
            try:
                request = requests.get('http://0.0.0.0:' + str(port_number) + '/checkstatus')

                if request.status_code == 200:
                    break
            
            except requests.exceptions.ConnectionError:
                pass

            time.sleep(0.01)

        time_passed = time.time() - start_time
        if port_number == 18081:
            print('creating time is ',time_passed)

    def create_benchmark(self,port_number):
        start_time = time.time()
        temp_container = self.client.containers.run('lzjzx1122/python3action_benchmark',command = 'python3 /actionProxy/apigateway.py',ports = {'18080/tcp': port_number},detach = True,stdin_open = True)

        #temp_container = self.client.containers.run('pzf/python3action',command = 'python3 /actionProxy/apigateway.py',ports = {'18080/tcp': port_number},detach = True,tty = True,stdin_open = True)

        temp_action_info = action_info(temp_container,port_number)
        self.instance_info[port_number-18081] = temp_action_info

        while True:
            try:
                request = requests.get('http://0.0.0.0:' + str(port_number) + '/checkstatus')

                if request.status_code == 200:
                    break

            except requests.exceptions.ConnectionError:
                pass

            time.sleep(0.01)

        time_passed = time.time() - start_time
        if port_number == 18081:
            print('creating time is ',time_passed)



    def code_loading(self,port_number):
        if port_number == 18081:
            print('before code loading : ',time.time()-self.instance_info[port_number-18081].start_time)
        
        #os.system('docker cp '+self.user_path+'/'+self.action_name+' '+self.instance_info[port_number-18081].container_id+':/action/')
        #self.instance_info[port_number-18081].container.exec_run("python3 /tmp/load_codes.py " + self.action_name)
        #os.system('docker exec ' + self.instance_info[port_number-18081].container_id + ' python3 /tmp/load_codes.py ' + self.action_name)
        
        os.system('curl http://0.0.0.0:'+str(port_number)+'/load_codes/'+self.action_name)
        if port_number == 18081:
            print('after code loading : ',time.time()-self.instance_info[port_number-18081].start_time)

    def run_check(self,port_number):
        os.system('curl http://0.0.0.0:'+str(port_number)+'/checkstatus')
        if port_number == 18081:
            print('------------Status checked !------------- ')

#    @asynci
    def run_action(self,port_number):
        #if port_number == 18081:
        #    print('before action run : ',time.time()-self.instance_info[port_number-18081].start_time)
        os.system('curl http://0.0.0.0:'+str(port_number)+'/actionrun/'+self.action_name)
        print('from ',port_number)
        #if port_number == 18081:
        #    print('after action run : ',time.time()-self.instance_info[port_number-18081].start_time)

    

    def remove(self,port_number):
        self.instance_info[port_number-18081].container.stop(timeout = 5)
        self.instance_info[port_number-18081].container.remove()
        self.instance_info[port_number-18081] = None
    
    def action_rent(self,container,port_number,renter_count): 
        #self.renter_instance_info[port_number-19081] = container.lender_instance_info[renter_count]
        st_time = time.time()
        self.renter_instance_info[port_number-18081] = container.instance_info[renter_count]
        container.instance_info[renter_count] = None
        print('rent time is ',time.time()-st_time)
        os.system('curl http://0.0.0.0:'+str(port_number)+'/load_codes/'+self.action_name)

    def lender_remove(self,port_number):
        self.lender_instance_info[port_number-19081].container.stop(timeout = 5)
        self.lender_instance_info[port_number-19081].container.remove()
        self.lender_instance_info[port_number-19081] = None
    
    def renter_remove(self,port_number):
        self.renter_instance_info[port_number-18081].container.stop(timeout = 5)
        self.renter_instance_info[port_number-18081].container.remove()
        self.renter_instance_info[port_number-18081] = None




