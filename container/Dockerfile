# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
FROM python:3.7-slim

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install ffmpeg

# fulfill the structure requirement of proxy
RUN mkdir /proxy && \
    mkdir /proxy/exec && \
    mkdir /proxy/actions

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

RUN pip install --no-cache-dir gevent flask

CMD [ "python", "/proxy/proxy.py" ]
