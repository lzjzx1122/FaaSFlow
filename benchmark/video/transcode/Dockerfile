FROM workflow_base

RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list
RUN cat /etc/apt/sources.list
RUN rm -Rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get -y --force-yes install yasm ffmpeg

COPY main.py /proxy/main.py
