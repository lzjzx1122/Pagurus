FROM action_linpack
COPY linpack.zip /proxy/actions/action_linpack.zip
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt && rm requirements.txt