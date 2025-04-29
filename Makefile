UNAME := $(shell uname)

ifeq ($(EXPLICIT_TAG),)
EXPLICIT_TAG := latest
endif
COMMIT_TAG   := $$(git log -1 --pretty=%h)

DL_APP_REMOTE_NAME  := digital-land-platform
REPO                := public.ecr.aws/l6z6v3j6
NAME                := $(REPO)/$(DL_APP_REMOTE_NAME)
COMMIT_IMG          := $(NAME):$(COMMIT_TAG)
EXPLICIT_IMG        := $(NAME):$(EXPLICIT_TAG)


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

piptool-install::
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

postgresql::
	sudo service postgresql start

insertBaseData::
	python -c 'from tests.utils.database import reset_database; reset_database()'
	python -c 'from tests.utils.database import *; add_base_entities_to_database(); add_base_datasets_to_database(); add_base_typology_to_database()'

emptyDatabase::
	python -c 'from tests.utils.database import reset_database; reset_database()'

server:
	echo $$OBJC_DISABLE_INITIALIZE_FORK_SAFETY
	gunicorn -w 2 -k uvicorn.workers.UvicornWorker application.app:app --preload --forwarded-allow-ips="*"

docker-build:
	docker build --build-arg RELEASE_TAG=$(COMMIT_TAG) --target production -t $(EXPLICIT_IMG) .
	docker tag $(EXPLICIT_IMG) $(COMMIT_IMG)

push: docker-login
	docker push $(COMMIT_IMG)
	docker push $(EXPLICIT_IMG)

login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(REPO)

docker-login:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

test-acceptance:
	echo SKIPPING

test-acceptance-debug:
	python -m playwright install --with-deps chromium firefox webkit
	PWDEBUG=1 python3 -m pytest --browser webkit --browser firefox --browser chromium --md-report --md-report-color=never -p no:warnings tests/acceptance

test-accessibility:
	python -m playwright install chromium
	python -m pytest --browser chromium --md-report --md-report-color=never -p no:warnings tests/accessibility

playwright-codegen:
	python -m playwright codegen --viewport-size=800,600 localhost:8000

test: test-unit test-integration test-acceptance test-accessibility

test-js:
	npm run test

test-js-unit:
	npm run test-unit

test-js-integration:
	npm run test-integration

test-unit:
	python -m pytest --md-report --md-report-color=never --md-report-output=unit-tests.md tests/unit
	npm run test-unit

test-integration:
	python -m pytest --md-report --md-report-color=never --md-report-output=integration-tests.md tests/integration
	npm run test-integration

test-integration-docker:
	docker-compose run web python -m pytest tests/integration --junitxml=.junitxml/integration.xml $(PYTEST_RUNTIME_ARGS)

lint:	black flake8

clean::
	rm -rf static/

stylesheets::
	npx nps build.stylesheets

govukAssets::
	npx nps copy.govukAssets

javascripts:
	npm run build
	rsync -r assets/javascripts static/

robots:
	cp assets/robots.txt static/robots.txt

frontend:
	npm i
	make javascripts
	make robots
	make stylesheets
	make govukAssets
	rsync -r assets/images static/
	cp node_modules/maplibre-gl/dist/maplibre-gl.css static/stylesheets/maplibre-gl.css
	mkdir -p static/govuk/assets
	cp node_modules/govuk-frontend/govuk/all.js node_modules/govuk-frontend/govuk/all.js.map static/govuk
	cp -r node_modules/govuk-frontend/govuk/assets/* static/govuk/assets

frontend-all: clean frontend

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

deploy: aws-deploy

aws-deploy:
ifeq (, $(ENVIRONMENT))
	$(error "No environment specified via $$ENVIRONMENT, please pass as make argument")
endif
	aws ecs update-service --force-new-deployment --service $(ENVIRONMENT)-web-service --cluster $(ENVIRONMENT)-web-cluster

.PHONY: docker-security-scan
docker-security-scan:
	mkdir -p zap-working-dir
	touch zap-working-dir/zap.log
	chmod -R a+rw zap-working-dir
	docker-compose \
		-f docker-compose.security.yml \
		run --rm zap
