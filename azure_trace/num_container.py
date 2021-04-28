import docker

cli = docker.from_env()

print(len(cli.containers.list()))