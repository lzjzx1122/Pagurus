FROM pagurus_base
COPY pip.conf /etc/pip.conf
COPY machine_learning.zip /proxy/actions/action_machine_learning.zip
RUN pip --no-cache-dir install numpy scipy joblib scikit-learn