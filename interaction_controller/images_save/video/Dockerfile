FROM pagurus_base
COPY pip.conf /etc/pip.conf
#COPY main.py /proxy/exec/main.py
#COPY outputvideo.mp4 /proxy/exec/outputvideo.mp4
COPY video.zip /proxy/actions/action_video.zip
RUN python -m pip install --upgrade pip
RUN pip3 --no-cache-dir install pillow scipy numpy scikit-video
