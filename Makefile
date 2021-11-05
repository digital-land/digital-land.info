include makerules/makerules.mk

CACHE_DIR=var/cache/
DOCKER_IMAGE_URL=955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web
UNAME := $(shell uname)

all::	lint

$(CACHE_DIR)organisation.csv:
	mkdir -p $(CACHE_DIR)
	curl -qfs "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv" > $(CACHE_DIR)organisation.csv

ifeq ($(UNAME), Darwin)
server: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
endif

init::
	pip install -e .[testing]
	npm install
	npm run build

server: $(CACHE_DIR)organisation.csv
	echo $$OBJC_DISABLE_INITIALIZE_FORK_SAFETY
	gunicorn -w 2 -k uvicorn.workers.UvicornWorker dl_web.app:app --preload --forwarded-allow-ips="*"

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

test-acceptance:
	python -m pytest -sv tests/acceptance

test-unit:
	python -m pytest -sv tests/unit

lint:	black-check flake8

generate-assets::
	npm run build
	npm run dev

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

server-dev:
	make -j 2 server generate-assets
