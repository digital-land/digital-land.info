UNAME := $(shell uname)

ifeq ($(EXPLICIT_TAG),)
EXPLICIT_TAG := latest
endif
COMMIT_TAG   := $$(git log -1 --pretty=%h)

# what if we tagged with commit sha?
REPO           := 955696714113.dkr.ecr.eu-west-2.amazonaws.com
NAME           := $(REPO)/digital-land-info
COMMIT_IMG     := $(NAME):$(COMMIT_TAG)
EXPLICIT_IMG   := $(NAME):$(EXPLICIT_TAG)

CF_APP_NAME := digital-land-platform

PUBLIC_REPO         := public.ecr.aws/l6z6v3j6
PUBLIC_NAME         := $(PUBLIC_REPO)/$(CF_APP_NAME)
PUBLIC_COMMIT_IMG   := $(PUBLIC_NAME):$(COMMIT_TAG)
PUBLIC_EXPLICIT_IMG := $(PUBLIC_NAME):$(EXPLICIT_TAG)


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

piptool-compile::
	python -m piptools compile --output-file=requirements/requirements.txt requirements/requirements.in
	python -m piptools compile requirements/dev-requirements.in


server:
	echo $$OBJC_DISABLE_INITIALIZE_FORK_SAFETY
	gunicorn -w 2 -k uvicorn.workers.UvicornWorker application.app:app --preload --forwarded-allow-ips="*"

build: docker-build-private docker-build-public

docker-build-private:
	docker build  --target production -t $(EXPLICIT_IMG) .
	docker tag $(EXPLICIT_IMG) $(COMMIT_IMG)

docker-build-public:
	docker build  --target production -t $(PUBLIC_EXPLICIT_IMG) .
	docker tag $(PUBLIC_EXPLICIT_IMG) $(PUBLIC_COMMIT_IMG)

push: push-private push-public

push-private: login
	docker push $(COMMIT_IMG)
	docker push $(EXPLICIT_IMG)

push-public: docker-login-public
	docker push $(PUBLIC_COMMIT_IMG)
	docker push $(PUBLIC_EXPLICIT_IMG)

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
	cf target -o dluhc-digital-land || cf login -a api.london.cloud.service.gov.uk

cf-deploy: cf-login
ifeq (, $(ENVIRONMENT))
	$(error "No environment specified via $$ENVIRONMENT, please pass as make argument")
endif
	cf target -o dluhc-digital-land -s $(ENVIRONMENT)
	cf push $(CF_APP_NAME)
