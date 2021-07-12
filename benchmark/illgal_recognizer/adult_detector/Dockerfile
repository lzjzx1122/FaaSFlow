FROM workflow_base

RUN pip3 install --no-cache-dir tensorflow keras pillow

COPY main.py /proxy/main.py
COPY resnet50_final_adult.h5 /proxy/resnet50_final_adult.h5