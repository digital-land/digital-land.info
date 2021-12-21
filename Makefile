DOCKER_IMAGE_URL=955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web
UNAME := $(shell uname)

all::	lint

ifeq ($(UNAME), Darwin)
server: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
endif

init::
	python -m pip install pip-tools
	python -m piptools sync requirements.txt dev-requirements.txt
	pre-commit install
	npm install

init:: frontend-all

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
	python -m pytest -p no:warnings tests/acceptance

test:
	python -m pytest --ignore=tests/acceptance

lint:	black-check flake8

clean::
	rm -rf static/

digital-land-frontend-init:
	npm run nps build.stylesheets
	npm run nps copy.javascripts
	npm run nps copy.images
	npm run nps copy.govukAssets

javascripts:
	npm run nps build.javascripts
	cp assets/javascripts/dl-national-map-controller.js static/javascripts/

frontend: javascripts
	npm run nps build.stylesheets
	rsync -r assets/images static/

frontend-all: clean digital-land-frontend-init frontend

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

server-dev:
	make -j 2 server generate-assets
