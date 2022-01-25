# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
FROM python:3.7-slim

COPY pip.conf /etc/pip.conf

# fulfill the structure requirement of proxy
RUN mkdir /proxy

# copy libs
COPY proxy.py /proxy/proxy.py
COPY main.py /proxy/main.py
COPY Store.py /proxy/Store.py
COPY container_config.py /proxy/container_config.py

WORKDIR /proxy

# proxy server runs under port 5000
EXPOSE 5000

# for alpine base only
# RUN apk update && \
#     apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev make && \
#     pip install --no-cache-dir gevent flask && \
#     apk del .build-deps

RUN apt-get clean
RUN apt-get update
RUN pip3 install --no-cache-dir gevent flask couchdb redis

CMD [ "python3", "/proxy/proxy.py" ]
