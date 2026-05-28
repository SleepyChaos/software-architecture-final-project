FROM python:3.11-slim

WORKDIR /app

COPY backbone/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backbone /app

EXPOSE 8000
