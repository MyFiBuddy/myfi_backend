# myfi_backend
This repo for performing Mutual Fund research, creating and managing portfolio and investing on mutual funds.
Code for API, celery tasks, workers and scheduler, docker local setup, continuous tests and CI using github actions and kubernetes deployment.


# Prerequisites
Install python3.11.6 and poetry(python dependency manager).

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m myfi_backend
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

You can stop the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . stop
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```

## Project structure

```bash
$ tree "myfi_backend"
myfi_backend
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifetime.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "MYFI_BACKEND_" prefix.

For example if you see in your "myfi_backend/settings.py" a variable named like
`random_parameter`, you should provide the "MYFI_BACKEND_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `myfi_backend.settings.Settings.Config`.

An example of .env file:
```bash
MYFI_BACKEND_RELOAD="True"
MYFI_BACKEND_PORT="8000"
MYFI_BACKEND_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/
## OpenTelemetry

If you want to start your project with OpenTelemetry collector
you can add `-f ./deploy/docker-compose.otlp.yml` to your docker command.

Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up
```

This command will start OpenTelemetry collector and jaeger.
After sending a requests you can see traces in jaeger's UI
at http://localhost:16686/.

This docker configuration is not supposed to be used in production.
It's only for demo purpose.

You can read more about OpenTelemetry here: https://opentelemetry.io/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possible bugs);

To run pre-commit checks simply run inside the shell:
```bash
pre-commit run --all-files
```

You can read more about pre-commit here: https://pre-commit.com/

## Kubernetes
To run your app in kubernetes
just run:
```bash
kubectl apply -f deploy/kube
```

It will create needed components.

If you haven't pushed to docker registry yet, you can build image locally.

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
docker save --output myfi_backend.tar myfi_backend:latest
```

## Migrations

Migration service will migrate db to latest state.

If you want to migrate your database, you should run following commands:
```bash
# To generate migration file for db update:
alembic revision --autogenerate --m "Add NewModel"

# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade head
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

To run tests locally:

1. Bring up local db by running:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
poetry run pytest -vv --cov="myfi_backend" .
```
OR
```bash
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=myfi_backend" -e "POSTGRES_USER=myfi_backend" -e "POSTGRES_DB=myfi_backend" postgres:alpine3.18
```

2. Run tests:
```bash
poetry run pytest -vv --cov="myfi_backend" .
```


## Running github actions locally

Read this article on how to run and test github actions locally.

https://github.com/nektos/act

e.g. to check the github action for pull_request
```bash
act pull_request --container-architecture linux/amd64
```
