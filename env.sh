#!/bin/bash

sudo apt-get update

sudo apt-get install git

curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

sudo apt install couchdb
service couchdb start

python3 -m pip install --upgrade pip

pip3 uninstall zipp

pip3 install -r requirements.txt
