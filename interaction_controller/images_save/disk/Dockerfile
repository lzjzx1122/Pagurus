FROM pagurus_base
                COPY disk.zip /proxy/actions/action_disk.zip
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt