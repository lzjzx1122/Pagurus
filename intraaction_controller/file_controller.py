import requests
import os
import shutil
import uuid

_action_dir_base = None
_storage_dir = None

_action_packages_dir_base = None
_packages_storage_dir = None

container_dir_id = {}

# initial job of file controller
def init(action_dir, storage_dir, action_packages_dir, packages_storage_dir):
    global _action_dir_base, _storage_dir, _action_packages_dir_base, _packages_storage_dir
    _action_dir_base = action_dir
    _storage_dir = storage_dir
    _action_packages_dir_base = action_packages_dir
    _packages_storage_dir = packages_storage_dir
    if os.path.exists(_storage_dir):
       shutil.rmtree(_storage_dir)
    os.mkdir(_storage_dir)
    if os.path.exists(_packages_storage_dir):
       shutil.rmtree(_packages_storage_dir)
    os.mkdir(_packages_storage_dir)

# create a directory for new container
# return container's directory
def create_dir():
    while True:
        dir_id = uuid.uuid4().hex
        path = os.path.join(_storage_dir, dir_id)
        packages_path = os.path.join(_packages_storage_dir, dir_id)
        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(packages_path)
            return (path, packages_path, dir_id)

# bind a directory id with a container id
# so that other function use container id instead of directory id
def bind(dir_id, container_id):
    container_dir_id[container_id] = dir_id

# get the directory path of container
def get_container_dir(container_id):
    return _container_dir(container_id)

def get_container_packages_dir(container_id):
    return _container_packages_dir(container_id)

# put action's code to container's directory
# action is action's name
def put_file_container(container_id, action):
    src = _action_dir(action)
    dst = os.path.join(_container_dir(container_id), action)
    shutil.copytree(src, dst)

def put_packages_container(container_id, action):
    src = _action_packages_dir(action)
    dst = os.path.join(_container_packages_dir(container_id), action)
    shutil.copytree(src, dst)

# remove all files in container's directory
def clean_container_dir(container_id):
    path = _container_dir(container_id)
    packages_path = _container_packages_dir(container_id)
    shutil.rmtree(path)
    shutil.rmtree(packages_path)
    os.mkdir(path)

# remove container's directory
def destroy_container_dir(container_id):
    path = _container_dir(container_id)
    packages_path = _container_packages_dir(container_id)
    shutil.rmtree(path)
    shutil.rmtree(packages_path)

def _action_dir(action_name):
    return os.path.join(_action_dir_base, action_name)

def _container_dir(container_id):
    return os.path.join(_storage_dir, container_dir_id[container_id])

def _action_packages_dir(action_name):
    return os.path.join(_action_packages_dir_base, action_name)

def _container_packages_dir(container_id):
    return os.path.join(_packages_storage_dir, container_dir_id[container_id])

