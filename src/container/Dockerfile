FROM python:3.7-slim
ENV PYTHONUNBUFFERED=1
#COPY pip.conf /etc/pip.conf
#RUN sed -i "s@http://deb.debian.org@http://mirrors.ustc.edu.cn@g" /etc/apt/sources.list
#RUN sed -i "s@http://security.debian.org@http://mirrors.ustc.edu.cn@g" /etc/apt/sources.list
#RUN sed -i "s@http://deb.debian.org@http://mirror.sjtu.edu.cn@g" /etc/apt/sources.list
#RUN sed -i "s@http://security.debian.org@http://mirror.sjtu.edu.cn@g" /etc/apt/sources.list
RUN mkdir /proxy
RUN mkdir /proxy/mnt
RUN mkdir /proxy/scripts
COPY block.py container_config.py proxy.py store.py bypass_store.py /proxy/
COPY scripts /proxy/scripts
WORKDIR /proxy
EXPOSE 5000

RUN apt clean
RUN apt update
RUN apt install -y iproute2
RUN pip3 install --no-cache-dir gevent flask requests couchdb redis gipc kafka-python confluent_kafka

CMD ["python3", "/proxy/proxy.py"]