FROM workflow_base

RUN apt-get clean
RUN apt-get update
RUN apt-get -y --force-yes --fix-missing install yasm ffmpeg

COPY main.py /proxy/main.py