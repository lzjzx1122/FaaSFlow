FROM codeless_base
RUN pip3 install --no-cache-dir googletrans==4.0.0-rc1
COPY config.py /proxy
RUN mkdir /blocks
COPY blocks /blocks
