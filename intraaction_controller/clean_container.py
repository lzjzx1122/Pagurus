import os
import docker

client = docker.from_env()
containers = client.containers.list()
for container in containers:
    if container.image.tags[0].startswith('pagurus_prewarm_base'):
        print('----Clearing ' + container.id + '----')
        os.system('docker rm -f ' + container.id)
    
