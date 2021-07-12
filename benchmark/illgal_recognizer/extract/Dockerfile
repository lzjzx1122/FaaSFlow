FROM workflow_base

RUN pip3 install --no-cache-dir pillow opencv-python

RUN apt-get update
RUN apt-get install tesseract-ocr

COPY main.py /proxy/main.py