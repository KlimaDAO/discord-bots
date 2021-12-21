FROM python:3.8-slim

# Install dependencies and do cleanup to save space
RUN apt-get update && \
    apt-get install -y \
    make \
    gcc \
    && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt

# We need to run the source code in the Docker image on Digital Ocean, so copy that in
# This is a public repo, so there is nothing proprietary that shouldn't be in the image
COPY src src
