DOCKER_IMAGE_URL=955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web
UNAME := $(shell uname)

all::	lint

ifeq ($(UNAME), Darwin)
server: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
endif

init::
	pip install -e .[testing]
	pre-commit install
	npm install

init:: digital-land-frontend-init

server:
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
	python -m playwright install chromium
	python -m pytest -p no:warnings -sv tests/acceptance

test:
	python -m pytest -sv tests/integration

lint:	black-check flake8

digital-land-frontend-init:
	npm run nps build.stylesheets
	npm run nps copy.javascripts
	npm run nps copy.json
	npm run nps copy.images
	npm run nps copy.govukAssets

frontend:
	npm run nps build.stylesheets
	rsync -r assets/images static/

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

server-dev:
	make -j 2 server generate-assets
