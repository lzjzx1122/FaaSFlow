# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
FROM python:3.7-slim

COPY pip.conf /etc/pip.conf

# fulfill the structure requirement of proxy
RUN mkdir /proxy && \
    mkdir /results

# copy the proxy server
COPY proxy.py /proxy/proxy.py

COPY function_utility/main.py /proxy/main.py

COPY function_utility/Store.py /proxy/Store.py

# the work dir of proxy is under exec/
WORKDIR /exec

# proxy server runs under port 5000
EXPOSE 5000

# for alpine base only
# RUN apk update && \
#     apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev make && \
#     pip install --no-cache-dir gevent flask && \
#     apk del .build-deps

RUN sed -i 's/deb.debian.org/mirror.sjtu.edu.cn/g' /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
RUN pip3 install --no-cache-dir gevent flask couchdb redis

# RUN pip3 install --no-cache-dir gevent flask couchdb redis tensorflow keras pillow opencv-python googletrans==4.0.0-rc1
# # ffmpeg
# RUN apt-get update
# RUN apt-get -y --force-yes install yasm ffmpeg tesseract-ocr

CMD [ "python3", "/proxy/proxy.py" ]
