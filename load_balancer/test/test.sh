# !/bin/zsh
sha1=`docker run -d -p 5001:5000 --name node1 jcdemo/flaskapp`
docker cp node1.py $sha1:/src/app.py

sha2=`docker run -d -p 5002:5000 --name node2 jcdemo/flaskapp`
docker cp node2.py $sha2:/src/app.py

sha3=`docker run -d -p 5003:5000 --name node3 jcdemo/flaskapp`
docker cp node3.py $sha3:/src/app.py

docker restart $sha1 $sha2 $sha3
