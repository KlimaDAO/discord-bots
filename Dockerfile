FROM python:3.8

RUN apt-get update && \
    apt-get install -y make

RUN mkdir -p /opt

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt

# We need to run the source code in the Docker image on Digital Ocean, so copy that in
# This is a public repo, so there is nothing proprietary that shouldn't be in the image
COPY src src
