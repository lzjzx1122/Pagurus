sudo apt-get update

# install docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# install couchdb in docker
sudo docker pull apache/couchdb:latest
sudo docker run -itd -p 5984:5984 -e COUCHDB_USER=openwhisk -e COUCHDB_PASSWORD=openwhisk --name couchdb couchdb

sudo apt install python3-pip -y

pip3 uninstall zipp

pip3 install gevent docker-compose asyncio couchdb numpy flask psutil

sudo apt install python3-virtualenv -y

# build base image
cd container
docker build --no-cache -t pagurus_base .
docker build --no-cache -t pagurus_base_repack .
cd ..

# build prewarm image
cd prewarm_container
docker build --no-cache -t pagurus_prewarm_base .
cd ..

# build images for functions
python3 interaction_controller/inter_controller.py build_images

# build virtualenv for prewarm
bash intraaction_controller/init_virtualenv.bash
