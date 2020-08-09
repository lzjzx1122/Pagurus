FROM pagurus_base

COPY linpack.zip /proxy/actions/action_linpack.zip
COPY requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt && rm requirement.txt
