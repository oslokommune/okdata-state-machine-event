# okdata-state-machine-event

Act on a cloudwatch rule when a step-function is done.

Will send an event to [status-api](https://github.com/oslokommune/dataplatform-status-api) with the appropriate status, based on the outcome of the step-function

## Setup

1. [Install Serverless Framework](https://serverless.com/framework/docs/getting-started/)
2. Install plugins:

```sh
make init
```

### Setup for development

```sh
python3.7 -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Code formatting

```sh
make format
```

## Running tests

```sh
$ make test
```

Tests are run using [tox](https://pypi.org/project/tox/).

## Deploy

Deploy to both dev and prod is automatic via GitHub Actions on push to main. You
can alternatively deploy from local machine (requires `saml2aws`) with: `make
deploy` or `make deploy-prod`.
