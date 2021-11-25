FROM workflow_base

RUN sed -i 's/deb.debian.org/mirrors.cloud.aliyuncs.com/g' /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y tesseract-ocr libgl1-mesa-glx

RUN pip3 install --no-cache-dir pillow opencv-python pytesseract

COPY main.py /proxy/main.py