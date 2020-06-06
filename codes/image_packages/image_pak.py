import json
import os
import numpy as np

class image_packages():
    def __init__(self,action_name,dockerfile_json,packages_json):
         self.action_name = action_name
         self.dockerfile = dockerfile_json
         self.packages = packages_json
         self.all_packages = {}
         self.all_dockerfile = {}
         self.candidates = {}
         self.renter = []
         self.save_path = ''

    def information_load(self):
        packages=open('build_file/packages_2.json',encoding='utf-8')
        packages_content=packages.read()
        self.all_packages = json.loads(packages_content)
        del self.all_packages[self.action_name]
        for (k1,v1) in self.packages.items():
            if v1 != 'default':
                for (k2,v2) in list(self.all_packages.items()):
                    if k1 in v2 :del self.all_packages[k2]
        
        for (k1,v1) in list(self.all_packages.items()):
            for (k2,v2) in list(v1.items()):
                if v2 != 'default' and k2 in self.packages:
                    del self.all_packages[k1]


        dockerfile=open('build_file/dockerfile.json',encoding='utf-8')
        dockerfile_content=dockerfile.read()
        self.all_dockerfile = json.loads(dockerfile_content)
        del self.all_dockerfile[self.action_name]

    def compare(self):
        cos_distance = []
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
            cos_distance.append(np.dot(vector_x,vector_y)/(np.linalg.norm(vector_x)*np.linalg.norm(vector_y)))
            vector_y = []
        #calculate the vector_y and cos distance
        print(cos_distance)

        candidates_list = list(self.candidates.keys())
        count = 0
        while cos_distance and count < 2:
            renter_id = cos_distance.index(max(cos_distance))
            if self.candidates[candidates_list[renter_id]] < 2:
                self.renter.append(candidates_list[renter_id])
                self.candidates[candidates_list[renter_id]] += 1
                count += 1
            else:pass
            del cos_distance[renter_id],candidates_list[renter_id]
        print(self.candidates)
        print(self.renter)
        
    def image_save(self):
        save_requirements = []
        for renter in self.renter:
            save_requirements.extend(self.all_dockerfile[renter].keys())
            save_requirements = list(set(save_requirements))
        print(save_requirements)
        self.save_path = 'images_save/'+self.action_name+'/'
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        file_write = open(self.save_path+'requirements.txt', 'w')
        for requirement in save_requirements:
            file_write.writelines(requirement+'\n')

        with open(self.save_path + 'Dockerfile', 'w') as f:
            f.write('FROM lzjzx1122/python3action_app_{}\n\n\
                    COPY requirements.txt /\n\n\
                    RUN pip3 install -r requirements.txt'.format(self.action_name))
        os.system('cd {} && docker build -t lzjzx1122/python3action_pack_{} .'.format(self.save_path, self.action_name))

test_name = 'k-means'
test_packages=open('build_file/packages_2.json',encoding='utf-8')
test_packages_content=test_packages.read()
test_packages_json = json.loads(test_packages_content)
test_dockerfile=open('build_file/dockerfile.json',encoding='utf-8')
test_dockerfile_content=test_dockerfile.read()
test_dockerfile_json = json.loads(test_dockerfile_content)
test_1 = test_packages_json[test_name]
test_2 = test_dockerfile_json[test_name]

test = image_packages(test_name,test_2,test_1)
test.information_load()
test.compare()
test.image_save()
