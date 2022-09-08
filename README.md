[![Build and deploy](https://github.com/digital-land/digital-land.info/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/digital-land/digital-land.info/actions/)
[![planning.data.gov.uk smoke test](https://github.com/digital-land/smoke-test/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/digital-land/smoke-test/actions/)

# planning.data.gov.uk web application

This is the repository for the [planning.data.gov.uk application](https://www.planning.data.gov.uk)

## Running locally

**Prerequisites**

    - python 3.8 or above
    - postgresql 13 or above with postgis extensions enabled


### Running the application

Create a virtualenv, then setup some environment variables. Copy `.env.example` to `.env`.

Note that to run tests you'll want a `.env.test` file as well to override db connection strings for local test. For
example, I have a digital_land_test db to run integration tests with and override \*\_DATABASE_URL variables using the
`.env.test` file.

### Install dependencies and other setup tasks

```
make init
```

That will install all dependencies, both python and node front end build tools as well as install pre-commit hooks.

The pre commit hooks will lint and run black and abort a commit on failure.  This will save you lots of broken builds
and subsequent "lint fix" commit messages.

### Postgres setup

**Mac users**

1. Install postgres using homebrew (see [https://wiki.postgresql.org/wiki/Homebrew]) or [PostgresApp](https://postgresapp.com/)

   Note any post install steps for how to get server running and adding command line tools to your path if required.

2. Once installed and running, from a terminal run:

   `createdb digital_land`

Then run the initial database migration from the root of this project (assuming)

    python -m alembic upgrade head

### Loading data into postgres

Assuming there's a running postgres available locally on localhost with a db called digital_land, you can
use [https://github.com/digital-land/digital-land-postgres](https://github.com/digital-land/digital-land-postgres) to
load entity data into the database.

Run the following command to load data into the database used by docker compose:

```
make load-db
```

Note that you will have to be authenticated with AWS ECR in order to pull the` ``digital-land-postgres` image. If you are following the [AWS Authentication](#aws-authentication) instructions from below, it would be better to run:

```
aws-vault exec dl-dev -- make load-db
```

Once the database is loaded, run `docker-compose up` to start the service with a fresh database

### Run integration tests

Setup a test database

    createdb digital_land_test

then you can run:

    make test

### Run the acceptance tests

This runs a browser based test of main pages, and a test of a json endpoint for an entity

    make test-acceptance

If you want to see the acceptance tests in action run the following:

    playwright install chromium
    python -m pytest tests/acceptance  --headed --slowmo 1000


--headed opens browser and --slowmo slows down interactions by the specified number of milliseconds

### Run the application


    make server

## Adding new python packages to the project

This project uses pip-tools to manage requirements files. [https://pypi.org/project/pip-tools/](https://pypi.org/project/pip-tools/)

When using fresh checkout of this repository, then make init will take care of the initial of packages from the checked
in requirements and dev-requirements files. These instructions are only for when you add new libraries to the project.

To add a production dependency to the main aapplication, add the package to [requirements.in](requirements.in)

    python -m piptools compile requirements/requirements.in

That will generate a new requirements.txt file

To add a development library, add a line to [dev-requirements.in](dev-requirements.in). Note that the first line of that file is:
"-c requirements.txt" which constrains the versions of dependencies in the requirements.txt file generated in previous step.

    python -m piptools compile requirements/dev-requirements.in

Then run

    python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

## Building the application container and restarting the service

Note that the Dockerfile for this application uses a multi-stage build. The production version can be built using the
target `production`. The target `dev` can be used to build a version for local development and is the version the
docker-compose file builds.

The docker container for use in production can be built with the following command (NB this tag can be anything):

In order to push the application container or deploy to the Planning Data AWS infrastructure you'll need to be authenticated.

### AWS Authentication

For the steps below [aws-vault](https://github.com/99designs/aws-vault) is used in order to assume the correct role for
accessing our AWS environment.

It is recommended to set something like this up, but you can get by with manual authentication or other tooling.
Just ensure that the various AWS env vars are setup such that you can use the aws cli as the `developer` role.
You can check this with the following command:

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

Once you are authenticated you can manage the application and container in ECR.



### Building the application container

```bash
docker build --target production -t digital-land-info .
```

Tag our build:

```bash
docker tag digital-land-info:latest 955696714113.dkr.ecr.eu-west-2.amazonaws.com/digital-land-info:latest
```

You need to have authenticated with AWS (see above) in order for docker push to work:

```bash
aws-vault exec dl-dev -- aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 955696714113.dkr.ecr.eu-west-2.amazonaws.com
```

Then we're finally ready to push the image:

```bash
docker push 955696714113.dkr.ecr.eu-west-2.amazonaws.com/digital-land-info
```

### Deployment

If you have pushed a new container, and want to initiate a deployment of the ECS service in order to start using it,
you can do so directly with an AWS command.

The command is:

```bash
aws-vault exec dl-dev -- aws ecs update-service --force-new-deployment --service development-web-service --cluster development-web-cluster
```

### Logging

The containers are configured to send their logs to AWS Cloudwatch. The log group is called `/development/digital-land-info`.

Logging configuration can be found in `log_config.yml`. Here you can change log level of each of the loggers independently, change the log format,
or redirect specific/all logs to file.

### Notes on docker compose

Docker compose can be used to run the application + database.

The docker-compose file uses the build target of `dev` for the main application, which has a multistage [Dockerfile](Dockerfile).

If you want to run tests using docker-compose, then a `.env.test` file may conflict with env vars in docker-compose file,
so it's probably best to make a decision about whether to run fully within the docker world locally or not, and stick
with one or the other.

**Build the containers:**

   docker-compose build

**Run up/down migrations:**

    docker-compose run --rm web python -m alembic upgrade head

**Downgrade last migration:**

    docker-compose run --rm web python -m alembic downgrade -1

**Run integration tests:**

    docker-compose run --rm db web python -m pytest tests/integration

**Run everything:**

    docker-compose up
