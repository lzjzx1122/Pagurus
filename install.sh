sudo apt-get update

curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

sudo docker pull apache/couchdb:latest

sudo docker run -itd -p 5984:5984 -e COUCHDB_USER=openwhisk -e COUCHDB_PASSWORD=openwhisk --name couchdb couchdb

sudo apt install python3-pip -y

pip3 uninstall zipp

pip3 install gevent docker-compose asyncio couchdb numpy flask psutil