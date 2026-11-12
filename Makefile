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

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show the available make targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-26s %s\n", $$1, $$2}'


all::	lint

ifeq ($(UNAME), Darwin)
server: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
endif

init:: ## Install deps (Python & JS), git hooks and frontend assets
	# Pinned pip version because stdlib_pkgs no longer works since the update to 26.2, breaking the pipeline
	python -m pip install --upgrade "pip==26.1.2" "pip-tools==7.6.0"
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt --pip-args "--no-cache-dir"
	python -m pre_commit install
	npm install

init:: frontend-all

piptool-compile::
	python -m piptools compile --output-file=requirements/requirements.txt requirements/requirements.in
	python -m piptools compile requirements/dev-requirements.in

piptool-upgrade::
	python -m piptools compile --upgrade --output-file=requirements/requirements.txt requirements/requirements.in
	python -m piptools compile --upgrade requirements/dev-requirements.in

piptool-install::
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

postgresql::
	sudo service postgresql start

insertBaseData::
	python -c 'from tests.utils.database import reset_database; reset_database()'
	python -c 'from tests.utils.database import *; add_base_entities_to_database(); add_base_organisations_to_database(); add_base_datasets_to_database(); add_base_typology_to_database(); add_base_provision_quality_to_database(); add_base_dataset_publication_to_database()'

emptyDatabase::
	python -c 'from tests.utils.database import reset_database; reset_database()'

server: ## Run the app locally (gunicorn + uvicorn workers)
	echo $$OBJC_DISABLE_INITIALIZE_FORK_SAFETY
	gunicorn -w 2 -k uvicorn.workers.UvicornWorker application.app:app --preload --forwarded-allow-ips="*"

docker-build: ## Build the production Docker image
	docker build --build-arg RELEASE_TAG=$(COMMIT_TAG) --target production -t $(EXPLICIT_IMG) .
	docker tag $(EXPLICIT_IMG) $(COMMIT_IMG)

push: docker-login
	docker push $(COMMIT_IMG)
	docker push $(EXPLICIT_IMG)

login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(REPO)

docker-login:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

test-acceptance: ## Run the Playwright acceptance tests
	python -m playwright install --with-deps chromium firefox webkit
	python -m pytest --browser webkit --browser firefox --browser chromium --md-report --md-report-color=never -p no:warnings tests/acceptance

test-acceptance-debug:
	python -m playwright install --with-deps chromium firefox webkit
	PWDEBUG=1 python3 -m pytest --browser webkit --browser firefox --browser chromium --md-report --md-report-color=never -p no:warnings tests/acceptance

test-accessibility: ## Run the accessibility tests
	python -m playwright install chromium
	python -m pytest --browser chromium --md-report --md-report-color=never -p no:warnings tests/accessibility

playwright-codegen:
	python -m playwright codegen --viewport-size=800,600 localhost:8000

test: test-unit test-integration test-acceptance test-accessibility ## Run all test suites

test-js:
	npm run test

test-js-unit:
	npm run test-unit

test-js-integration:
	npm run test-integration

test-unit: ## Run the unit tests
	python -m pytest --md-report --md-report-color=never --md-report-output=unit-tests.md tests/unit
	npm run test-unit

test-integration: ## Run the integration tests
	python -m pytest --md-report --md-report-color=never --md-report-output=integration-tests.md tests/integration
	npm run test-integration

test-integration-docker:
	docker-compose run web python -m pytest tests/integration --junitxml=.junitxml/integration.xml $(PYTEST_RUNTIME_ARGS)

lint:	black flake8 ## Format and lint the code (black + flake8)

clean:: ## Remove built static assets
	rm -rf static/

stylesheets::
	npx nps build.stylesheets

govukAssets::
	npx nps copy.govukAssets

javascripts:
	npm run build
	rsync -r assets/javascripts static/

frontend: ## Build the frontend assets
	npm i
	make javascripts
	make stylesheets
	make govukAssets
	rsync -r assets/images static/
	cp node_modules/maplibre-gl/dist/maplibre-gl.css static/stylesheets/maplibre-gl.css

frontend-all: clean frontend

watch-stylesheets:
	npx sass assets/stylesheets/application.scss:static/stylesheets/application.css --load-path=node_modules --watch

watch-javascripts:
	@echo "Starting JavaScript watch (rollup + file sync)..."
	@npm run build -- --watch & \
	while true; do \
		rsync -r assets/javascripts static/; \
		if command -v fswatch >/dev/null 2>&1; then \
			fswatch -1 -r assets/javascripts; \
		else \
			sleep 2; \
		fi; \
	done

frontend-watch:
	@echo "Starting frontend watch (stylesheets + javascripts)..."
	@make -j 2 watch-stylesheets watch-javascripts

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

server-dev: ## Run the app with live frontend rebuild
	make -j 2 server frontend-watch

load-db: login ## Load a database dump locally (docker-compose)
	docker-compose -f docker-compose.yml -f docker-compose.load-db.yml run load-db-dataset
	docker-compose -f docker-compose.yml -f docker-compose.load-db.yml run load-db-entity

deploy: aws-deploy ## Force a new ECS deployment (ENVIRONMENT required)

aws-deploy:
ifeq (, $(ENVIRONMENT))
	$(error "No environment specified via $$ENVIRONMENT, please pass as make argument")
endif
	aws ecs update-service --force-new-deployment --service $(ENVIRONMENT)-web-service --cluster $(ENVIRONMENT)-web-cluster

.PHONY: docker-security-scan
docker-security-scan: ## Run the OWASP ZAP dynamic scan (needs the image)
	mkdir -p zap-working-dir
	touch zap-working-dir/zap.log
	chmod -R a+rw zap-working-dir
	docker-compose \
		-f docker-compose.security.yml \
		run --rm zap

# locust tests will be run against the following host:
TEST_HOST ?= http://localhost:8000

test-load-website:
	locust -f tests/load/website_test.py -H $(TEST_HOST) -t 5m
test-load-map:
	locust -f tests/load/map_test.py -H $(TEST_HOST) -t 5m
test-load-dataset:
	locust -f tests/load/dataset_test.py -H $(TEST_HOST) -t 5m
test-load-entity:
	locust -f tests/load/entity_test.py -H $(TEST_HOST) -t 5m
test-load-entity-random:
	locust -f tests/load/entity_rand_test.py -H $(TEST_HOST) -t 5m -T random
test-load-entity-static-pool:
	locust -f tests/load/entity_rand_test.py -H $(TEST_HOST) -t 5m -E random -T static
test-load-cache-warmup:
	locust -f tests/load/cache_warmup_test.py -H $(TEST_HOST) -t 10m -u 3 -r 1 --headless

.PHONY: scan docker-scan

SEMGREP_VERSION = 1.183.0
SEMGREP_IMAGE = semgrep/semgrep:$(SEMGREP_VERSION)
# Shared args so `scan` and `scan-docker` stay identical. Fails on high/critical
# (ERROR-severity) findings only.
SEMGREP_ARGS = scan --config p/python --config p/secrets --config p/javascript --config p/dockerfile --config p/github-actions --severity ERROR --error --metrics=off

# scan        - native, needs `pip install semgrep==$(SEMGREP_VERSION)`
# docker-scan - containerised, needs only Docker
scan: ## Static security scan (SAST); fails on high/critical
	semgrep $(SEMGREP_ARGS)

docker-scan: ## Static security scan in Docker (no local install)
	docker run --rm -v $(CURDIR):/src -w /src $(SEMGREP_IMAGE) semgrep $(SEMGREP_ARGS)
