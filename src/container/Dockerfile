# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
FROM python:3.7-slim

COPY pip.conf /etc/pip.conf

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

RUN pip3 install --no-cache-dir gevent flask

CMD [ "python3", "/proxy/proxy.py" ]
