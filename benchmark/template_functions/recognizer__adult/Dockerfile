FROM codeless_base
RUN pip3 install --no-cache-dir tensorflow keras pillow
COPY config.py /proxy
RUN mkdir /blocks
COPY blocks /blocks
COPY resnet50_final_adult.h5 /proxy/resnet50_final_adult.h5