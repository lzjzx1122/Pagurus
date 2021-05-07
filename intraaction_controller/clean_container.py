import os
import docker

client = docker.from_env()
containers = client.containers.list()
for container in containers:
    if container.name != 'couchdb_workflow':
        container.remove(force=True)