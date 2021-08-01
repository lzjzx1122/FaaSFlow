FROM workflow_base

RUN apt-get update
RUN apt-get -y --force-yes install yasm ffmpeg

COPY main.py /proxy/main.py
COPY sample.mp4 /proxy/sample.mp4