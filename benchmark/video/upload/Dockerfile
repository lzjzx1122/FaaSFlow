FROM workflow_base

RUN apt-get clean
RUN apt-get update
RUN apt-get -y --force-yes install yasm ffmpeg

COPY main.py /proxy/main.py
COPY test.mp4 /proxy/test.mp4