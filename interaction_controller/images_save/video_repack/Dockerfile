FROM action_video
                    COPY video.zip /proxy/actions/action_video.zip
                    COPY requirements.txt .
                    RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt