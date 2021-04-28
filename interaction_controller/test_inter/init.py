import os
import docker

client = docker.from_env()
containers = client.containers.list()
for container in containers:
    if container.name != 'couchdb_workflow':
        container.remove(force=True)

'''
os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/action_results")
os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/inter_results")
os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/lend_info")
os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/renter_lender_info")
os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/container")
'''
'''
os.system('docker rmi $(docker images | grep "none" | awk \'{print $3}\')')
os.system('docker rm $(docker ps -a | grep \"' + 'pagurus_base' + '\" | awk \'{print $1}\')')
docker rm $(docker ps -a | grep 'pagurus_base' | awk '{print $1}')
# actions = ["image", "network", "video", "float_operation", "disk", "linpack", "matmul", "map_reduce", "couchdb_test", "markdown2html", "k-means"]
#actions = ['utility0', 'utility1', 'utility2', 'utility3', 'utility4', 'utility5', 'utility6', 'utility7', 'utility8', 'utility9', 'utility10', 'utility11', 'utility12', 'utility13', 'utility14', 'utility15', 'utility16', 'utility17', 'utility18', 'utility19']
for i in range(776):
    action = 'utility' + str(i)
    os.system('docker stop $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + 'action_' + action + '_repack' + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + 'action_' + action + '_repack' + '\" | awk \'{print $1}\')')
'''