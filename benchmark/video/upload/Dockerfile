FROM workflow_base

RUN sed -i 's/deb.debian.org/mirrors.cloud.aliyuncs.com/g' /etc/apt/sources.list
RUN apt-get clean

RUN apt-get update
RUN apt-get -y --force-yes install yasm ffmpeg

COPY main.py /proxy/main.py
COPY test.mp4 /proxy/test.mp4