FROM triggerflow/ibm_cloud_functions_runtime-v36:0.2

ENV FLASK_PROXY_PORT 8080

RUN apt-get update && apt-get upgrade -y

RUN     apt-get install -y \
        build-essential \
        gcc \
        grass \
    	grass-dev \
    	libc-dev \
        libxslt-dev \
        libxml2-dev \
        libffi-dev \
        libssl-dev \
        zip \
        unzip \
        vim \
        libgdal-dev \
        gdal-bin \
        && rm -rf /var/lib/apt/lists/*

RUN apt-cache search linux-headers-generic

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip setuptools six && pip install --no-cache-dir -r requirements.txt
