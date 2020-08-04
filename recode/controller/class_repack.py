import json
import os
import numpy as np

class repack_controller():
    def __init__(self):
        self.action_name = ''
        self.docker_file = {}
        self.packages = {}
        self.all_packages = {}
        self.all_docker_file = {}
        self.candidates = {}
        self.renter = {}
        self.share_action_number = 0
        self.save_path = ''

    def packages_reload(self):
        all_packages = open('build_file/packages.json',encoding='utf-8')
        all_packages_content=all_packages.read()
        self.all_packages = json.loads(all_packages_content)
        all_docker_file=open('build_file/docker_file.json',encoding='utf-8')
        all_docker_file_content=all_docker_file.read()
        self.all_docker_file = json.loads(all_docker_file_content)
    
    def action_repack(self,action_name,docker_file_json,packages_json,share_action_number=2):
        self.action_name = action_name
        self.docker_file = docker_file_json
        self.packages = packages_json
        self.all_packages.pop(self.action_name)
        self.all_docker_file.pop(self.action_name)
        self.share_action_number = share_action_number
        self.renter = {}
        self.candidates = {}
        for (k1,v1) in self.packages.items():
                for (k2,v2) in list(self.all_packages.items()):
                    if (k1 in v2) and (v2[k1] != v1):
                        self.all_packages.pop(k2)
        packages_vector = []
        vector_x,vector_y = [],[]
        for (k1,v1) in self.packages.items(): 
            for (k2,v2) in self.all_packages.items():
                if v2.__contains__(k1) and (k2 not in self.candidates.keys()):
                    self.candidates[k2] = 0
                    packages_vector.extend(v2.keys())
                    packages_vector = list(set(packages_vector))
        #list all the packages that contain child set
        for x in packages_vector:
            if x in self.packages.keys():
                vector_x.append(1)
            else:vector_x.append(0)
        #calculate the vector_x
        for candidate in self.candidates.keys():
            for x in packages_vector:
                if x in self.all_packages[candidate].keys():
                    vector_y.append(1)
                else:vector_y.append(0)    
            self.candidates[candidate] = (np.dot(vector_x,vector_y)/(np.linalg.norm(vector_x)*np.linalg.norm(vector_y)))
            vector_y = []
        #calculate the vector_y and cos distance
        while self.candidates and self.share_action_number > 0:
            renter_id = max(self.candidates, key=self.candidates.get)
            self.renter.update({renter_id:self.candidates[renter_id]})
            self.candidates.pop(renter_id)
            self.share_action_number -= 1
        #print(self.renter,self.candidates)
        return self.action_name, self.renter

    def image_save(self):
        save_requirements = []
        for renter in self.renter.keys():
            save_requirements.extend(self.all_docker_file[renter].keys())
            save_requirements = list(set(save_requirements))
        self.save_path = 'images_save/'+self.action_name+'/'
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        file_write = open(self.save_path+'requirements.txt', 'w')
        for requirement in save_requirements:
            file_write.writelines(requirement+'\n')

        with open(self.save_path + 'Dockerfile', 'w') as f:
            f.write('FROM lzjzx1122/python3action{}\n\n\
                    COPY requirements.txt /\n\n\
                    RUN pip3 install -r requirements.txt'.format(self.action_name))
        #os.system('cd {} && docker build -t lzjzx1122/python3action_pack_{} .'.format(self.save_path, self.action_name))
        

        #加一个与原文件比较，若相同，则跳过此步骤。


# test_name = 'image'
# test = repack_controller()
# test.packages_reload()
# lender, renter = test.action_repack(test_name,{1:1},{"pillow":"default"},3)
# test.image_save()
