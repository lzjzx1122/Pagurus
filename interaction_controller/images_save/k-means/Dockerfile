FROM pagurus_base
COPY pip.conf /etc/pip.conf
COPY k-means.zip /proxy/actions/action_k-means.zip
RUN pip3 --no-cache-dir install sklearn joblib pandas scikit-learn scipy