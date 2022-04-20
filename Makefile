UNAME := $(shell uname)

# what if we tagged with commit sha?
REPO=955696714113.dkr.ecr.eu-west-2.amazonaws.com
NAME=$(REPO)/digital-land-info
TAG    := $$(git log -1 --pretty=%h)
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest

CF_APP_NAME := digital-land-platform

PUBLIC_REPO   := public.ecr.aws/l6z6v3j6
PUBLIC_NAME   := $(PUBLIC_REPO)/$(CF_APP_NAME)
PUBLIC_TAG    := $$(git log -1 --pretty=%h)
PUBLIC_IMG    := ${PUBLIC_NAME}:${PUBLIC_TAG}


all::	lint

ifeq ($(UNAME), Darwin)
server: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
endif

init::
	python -m pip install pip-tools
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt
	python -m pre_commit install
	npm install

init:: frontend-all

server:
	echo $$OBJC_DISABLE_INITIALIZE_FORK_SAFETY
	gunicorn -w 2 -k uvicorn.workers.UvicornWorker application.app:app --preload --forwarded-allow-ips="*"

build: docker-build

docker-build:
	docker build  --target production -t ${IMG} .
	docker tag ${IMG} ${LATEST}
	docker tag ${IMG} ${PUBLIC_IMG}

push: push-private push-public

push-private: login
	docker push ${NAME}

push-public: docker-login-public
	docker push $(PUBLIC_NAME)

login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(REPO)

docker-login-public:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

test-acceptance:
	python -m playwright install chromium
	python -m pytest -p no:warnings tests/acceptance

test: test-unit test-integration

test-unit:
	python -m pytest tests/unit --junitxml=.junitxml/unit.xml

test-integration:
	python -m pytest tests/integration --junitxml=.junitxml/integration.xml

test-integration-docker:
	docker-compose run web python -m pytest tests/integration --junitxml=.junitxml/integration.xml $(PYTEST_RUNTIME_ARGS)

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

frontend-watch:
	npm run nps watch.assets & npm run nps watch.pages

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

server-dev:
	make -j 2 server frontend-watch

load-db: login
	docker-compose -f docker-compose.yml -f docker-compose.load-db.yml run load-db-dataset
	docker-compose -f docker-compose.yml -f docker-compose.load-db.yml run load-db-entity

cf-login:
	cf login -a api.london.cloud.service.gov.uk -u $(CF_USERNAME)

cf-deploy:
	cf target -o dluhc-digital-land -s $(ENVIRONMENT)
	cf push $(CF_APP_NAME) --docker-image $(PUBLIC_IMG)
	set -a; source ./.env.$(ENVIRONMENT); set +a
	cf set-env $(CF_APP_NAME) ENVIRONMENT $(ENVIRONMENT)
	cf set-env $(CF_APP_NAME) DATASETTE_URL $(DATASETTE_URL)
	cf set-env $(CF_APP_NAME) S3_COLLECTION_BUCKET $(S3_COLLECTION_BUCKET)
	cf set-env $(CF_APP_NAME) S3_HOISTED_BUCKET $(S3_HOISTED_BUCKET)
	cf set-env $(CF_APP_NAME) WRITE_DATABASE_URL $(WRITE_DATABASE_URL)
	cf set-env $(CF_APP_NAME) READ_DATABASE_URL $(READ_DATABASE_URL)
