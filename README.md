[![Build and deploy](https://github.com/digital-land/digital-land.info/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/digital-land/digital-land.info/actions/)
[![Digital land smoke test](https://github.com/digital-land/smoke-test/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/digital-land/smoke-test/actions/)


# AWS Authentication

Throughout this guide, [aws-vault](https://github.com/99designs/aws-vault) is used in order to assume the correct role for accessing our AWS environment. It is recommended to set something like this up, but you can get by with manual authentication or other tooling. Just ensure that the various AWS env vars are setup such that you can use the aws cli as the `developer` role. You can check this with the following command:

```bash
aws sts get-caller-identity
```

If everything is configured correctly this should return the details of the `developer` role (account `955696714113` at time of writing)

```json
{
    "UserId": <REDACTED>,
    "Account": "955696714113",
    "Arn": "arn:aws:sts::955696714113:assumed-role/developer/<REDACTED>"
}
```

# Running locally

Create a virtualenv then

```
make init
```

That will install all dependencies as well as install pre-commit hooks.

The pre commit hooks will  lint and run black and abort a commit on failure.

This will save you lots of broken builds and subsequent "lint fix" commit messages.

Run integration tests

```
make test
```

Run the acceptance tests

This runs a browser based test of main pages, and a test of a json endpoint for an entity

```
make test-acceptance
```

If you want to see the acceptance tests in action run the following:

```
playwright install chromium
pytest tests/acceptance  --headed --slowmo 1000
```

--headed opens browser and --slowmo slows down interactions by the specified number of milliseconds

To run the app use:

```
make server
```

### Adding new python packages to the project

This project uses pip-tools to manage requirements files. [https://pypi.org/project/pip-tools/](https://pypi.org/project/pip-tools/)

When using fresh checkout of this repository, then make init will take care of the initial of packages from the checked
in requirements and dev-requirements files. These instructions are only for when you add new libraries to the project.

To add a production dependency to the main aapplication, add the package to [requirements.in](requirements.in)

    python -m piptools compile requirements/requirements.in

That will generate a new requirements.txt file

To add a development library, add a line to [dev-requirements.in](dev-requirements.in). Note that the first line of that file is:
"-c requirements.txt" which constrains the versions of dependencies in the requirements.txt file generated in previous step.

    python -m piptools compile requiements/dev-requirements.in

Then run

    python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt




# Building the application container

The docker container can be built with the following command (NB this tag can be anything):

```bash
docker build --target production -t dl_web_container .
```

Tag our build:

```bash
docker tag dl_web_container:latest 955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web:latest
```

Authenticate with AWS in order for docker push to work:

```bash
aws-vault exec dl-dev -- aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 955696714113.dkr.ecr.eu-west-2.amazonaws.com
```

Then we're finally ready to push the image:

```bash
docker push 955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web
```

# Force redeployment

If you have pushed a new container, and want to force a redeployment of the ECS service in order to start using it, you can do so directly with aws and do not need to use terraform. The command is:

```bash
aws-vault exec dl-dev -- aws ecs update-service --force-new-deployment --service development-ecs-service --cluster development-ecs-cluster
```

# Logging

The containers are configured to send their logs to AWS Cloudwatch. The log group is called `/development/dl-web`.

Logging configuration can be found in `log_config.yml`. Here you can change log level of each of the loggers independently, change the log format, or redirect specific/all logs to file.


### Notes on docker compose

Docker compose can be used to run the application + database. It uses the build target of dev for the main application,
which has a multistage [Dockerfile](Dockerfile)

Run up/down migrations

    docker-compose run --rm web python -m alembic upgrade head

Downgrade last migration

    docker-compose run --rm web python -m alembic downgrade -1

Run integration tests

    docker-compose run --rm web python -m pytest tests/integration
