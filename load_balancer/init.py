import os
import couchdb

os.system("curl -X DELETE http://openwhisk:openwhisk@172.20.185.118:5984/action_results")
os.system("curl -X DELETE http://openwhisk:openwhisk@172.20.185.118:5984/inter_results")
os.system("curl -X DELETE http://openwhisk:openwhisk@172.20.185.118:5984/lend_info")
os.system("curl -X DELETE http://openwhisk:openwhisk@172.20.185.118:5984/renter_lender_info")
os.system("curl -X DELETE http://openwhisk:openwhisk@172.20.185.118:5984/container")

'''
actions = ["image", "network", "video", "float_operation", "disk", "linpack", "matmul", "map_reduce", "couchdb_test", "markdown2html", "k-means"]

for action in actions:
    # print('docker stop $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + 'action_' + action + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + 'action_' + action + '_repack' + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + 'action_' + action + '_repack' + '\" | awk \'{print $1}\')')

images = ['852d67449fc2', '77cbcfc2537c']
for image in images:
    # print('docker stop $(docker ps -a | grep \"' + image + '\" | awk \'{print $1}\')')
    os.system('docker stop $(docker ps -a | grep \"' + image + '\" | awk \'{print $1}\')')
    os.system('docker rm $(docker ps -a | grep \"' + image + '\" | awk \'{print $1}\')')
'''

server = couchdb.Server('http://openwhisk:openwhisk@172.20.185.118:5984')
server.create('action_results')
server.create('inter_results')
server.create('lend_info')
server.create('renter_lender_info')
server.create('container')
