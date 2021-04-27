# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
# FROM docker.io/valian/docker-python-opencv-ffmpeg:py3
FROM python:3.7-slim
# FROM docker.io/jrottenberg/ffmpeg:4.1-alpine

COPY pip.conf /etc/pip.conf

# RUN apt-get -y update && \
#    apt-get -y upgrade

# RUN apt-get -y install gpg

# RUN apt-key adv –keyserver keyserver.ubuntu.com –recv-keys 3B4FE6ACC0B21F32

# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 40976EAF437D05B5
# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32

# COPY sources.list /etc/apt/sources.list

# RUN apt-get -y update && \
#    apt-get -y upgrade

# RUN apt-get -y install ffmpeg

# fulfill the structure requirement of proxy
RUN mkdir /proxy && \
    mkdir /proxy/exec

# copy the proxy server
COPY proxy.py /proxy/

# the work dir of proxy is under exec/
WORKDIR /proxy/exec

# proxy server runs under port 5000
EXPOSE 5000

# for alpine base only
# RUN apk update && \
#     apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev make && \
#     pip install --no-cache-dir gevent flask && \
#     apk del .build-deps

RUN pip3 install --no-cache-dir gevent flask

CMD [ "python3", "/proxy/proxy.py" ]
