import os

os.system("curl -X DELETE http://openwhisk:openwhisk@127.0.0.1:5984/action_results")

actions = ["image", "network", "video", "float_operation", "disk", "linpack", "matmul", "map_reduce", "couchdb_test", "markdown2html", "k-means"]

for action in actions:
    # print('docker stop $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + 'action_' + action + '_repack' + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + 'action_' + action + '_repack' + '\" | awk \'{print $1}\')')


'''
images = ['c8938e200a0b', '81b56c62fd8f', '8c0f7d83e74b']
for image in images:
    # print('docker stop $(docker ps -a | grep \"' + image + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + image + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + image + '\" | awk \'{print $1}\')')
'''   