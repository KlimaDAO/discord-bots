DOCKER_USER=klimadao
DOCKER_IMAGE=discord-bots
DOCKER_TAG=latest

build:
	docker build -t $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG) .