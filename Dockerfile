FROM python:3.13.3-alpine

EXPOSE 8800
WORKDIR /app

COPY requirements.txt /tmp/

RUN python3 -m pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY app.py /app/app.py

ENTRYPOINT [ "fastapi", "run" ]
