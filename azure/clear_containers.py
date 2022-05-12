import os
import docker

client = docker.from_env()
containers = client.containers.list()
for container in containers:
    # print(container.name)
    if container.name != 'couchdb':
        container.remove(force=True)

os.system('docker rm $(docker ps -a -q)')
