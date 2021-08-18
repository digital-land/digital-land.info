include makerules/makerules.mk

CACHE_DIR=var/cache/
DOCKER_IMAGE_URL=955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web

$(CACHE_DIR)organisation.csv:
	mkdir -p $(CACHE_DIR)
	curl -qfs "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv" > $(CACHE_DIR)organisation.csv

server: $(CACHE_DIR)organisation.csv
	# python -m dl_web.app
	uvicorn dl_web.app:app --reload --workers 10

build:
	docker build -t $(DOCKER_IMAGE_URL) .

push:
	docker push $(DOCKER_IMAGE_URL)

login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(DOCKER_IMAGE_URL)

plan:
	cd tf/app; terraform plan -out=tfplan

apply:
	cd tf/app; terraform apply tfplan

test:
	python -m pytest -sv

lint:
	black --check .
	flake8 .
