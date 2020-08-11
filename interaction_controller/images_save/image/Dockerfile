FROM pagurus_base
                COPY image.zip /proxy/actions/action_image.zip
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt