FROM workflow_base

RUN sed -i 's/deb.debian.org/mirror.sjtu.edu.cn/g' /etc/apt/sources.list
RUN apt-get clean

RUN apt-get update
RUN apt-get -y --force-yes install yasm ffmpeg

COPY main.py /proxy/main.py
COPY test.mp4 /proxy/test.mp4