FROM python:3.8

RUN apt-get update && \
    apt-get install -y make

RUN mkdir -p /opt

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt
