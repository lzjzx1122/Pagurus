import os
import docker
import time
import requests
import json

class container_info():
    def __init__(self,container,port_number):
        self.container = container
        self.container_id = container.id
        self.port_number = port_number
        self.out = ''
        self.start_time = time.time()
#对应每个容器的信息，port_number为当前容器对应的端口号，start_time为容器创建时间

class packages_info():
    def __init__(self):
        self.packages = {}
        self.dockerfile = {}
#对应每个action依赖包的信息，packages为容器中实际增加的包，dockerfile为用户指定安装的包

    def update(self,action_name,user_path):
        temp_packages=open(user_path+'/buildfile/packages.json',encoding='utf-8')
        temp_packages_content=temp_packages.read()
        temp_dockerfile=open(user_path+'/buildfile/dockerfile.json',encoding='utf-8')
        temp_dockerfile_content=temp_dockerfile.read()
        self.packages = json.loads(temp_packages_content)
        self.dockerfile = json.loads(temp_dockerfile_content)

class action_create():
    def __init__(self,port_number,user_path,action_name,max_containers,share_count):
        self.start_port_number = port_number
        self.client = docker.from_env()
        self.user_path = user_path
        self.action_name = action_name
        self.share_count = share_count
        self.max_containers = max_containers
        self.current_containers = 0
        self.packages_info = packages_info()
        self.packages_info.update(self.action_name,self.user_path)
        self.instance_info = [None for index in range(max_containers)]
        self.renter_instance_info = [None for index in range(max_containers)]
        self.lender_instance_info = [None for index in range(share_count)]
#对应每个action的信息，start_port_number对应当前action可创建容器的对应起始端口号，max_container为最大可创建容器数量（则当前容器可开放的端口号对应为[start_port_number,start_port_number_max_containers]）
#，user_path则为action文件存储的位置，share_count为当前可共享的容器数量。
    def container_create(self,startup_type,port_number):
        if startup_type == 'repack':
            temp_container = self.client.containers.run('lzjzx1122/python3action_pack_'+self.action_name,command = 'python3 /actionProxy/apigateway.py',ports = {'18080/tcp': port_number},detach = True,stdin_open = True)
            temp_action_info = container_info(temp_container,port_number)
            self.lender_instance_info[port_number-self.start_port_number] = temp_action_info
        else: 
            temp_container = self.client.containers.run('lzjzx1122/python3action_benchmark',command = 'python3 /actionProxy/apigateway.py',ports = {'18080/tcp': port_number},detach = True,stdin_open = True)
            temp_action_info = container_info(temp_container,port_number)
            self.instance_info[port_number-self.start_port_number] = temp_action_info
        while True:
            try:
                request = requests.get('http://0.0.0.0:' + str(port_number) + '/checkstatus')

                if request.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.01)

packages_info_test = packages_info()
packages_info_test.update('video','/home/openwhisk/pagurus/recode/actions/video')
print(packages_info_test.packages,packages_info_test.dockerfile)      