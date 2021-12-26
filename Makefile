DOCKER_USER=klimadao
DOCKER_IMAGE=discord-bots
DOCKER_TAG=latest
DOCKER_IMAGE_DEPLOY=discord-bots-deploy
DOCKER_TARGET_BASE=--target base
DOCKER_TARGET_DEPLOY=--target deploy
DOCKER_DEPLOY_ENV=-e DIGITALOCEAN_ACCESS_TOKEN=$(DIGITALOCEAN_ACCESS_TOKEN)

build:
	docker build $(DOCKER_TARGET_BASE) -t $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG) .

build_deploy:
	docker build $(DOCKER_TARGET_DEPLOY) -t $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) .

shell: build
	docker run -it --rm $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG) /bin/bash

shell_deploy: build_deploy
	@[ "${DIGITALOCEAN_ACCESS_TOKEN}" ] || ( echo "DIGITALOCEAN_ACCESS_TOKEN must be set in order to deploy"; exit 1 )
	docker run -it --rm $(DOCKER_DEPLOY_ENV) $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) /bin/bash

deploy: build_deploy
	@[ "${DIGITALOCEAN_ACCESS_TOKEN}" ] || ( echo "DIGITALOCEAN_ACCESS_TOKEN must be set in order to deploy"; exit 1 )
	docker run -it --rm $(DOCKER_DEPLOY_ENV) $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) bash -c 'doctl apps create --upsert --spec app-spec.yml --wait --verbose'
