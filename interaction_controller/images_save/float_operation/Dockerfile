FROM pagurus_base
                COPY float_operation.zip /proxy/actions/action_float_operation.zip
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt