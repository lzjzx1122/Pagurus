FROM action_k-means
COPY pip.conf /etc/pip.conf
COPY linpack.zip /proxy/actions/action_linpack.zip
COPY disk.zip /proxy/actions/action_disk.zip
RUN pip3 --no-cache-dir install numpy