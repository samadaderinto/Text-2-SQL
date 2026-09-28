# AudQL

This is the system that powers the entire AudQL infrastructure. The AudQL backend is a dockerized  Django and Django rest framework application. The bucket application runs in two modes;  the production mode "prod"  and the development mode "dev". 

## Testing

Install the test dependencies and run the backend unit and API integration tests
from the `server` directory:

```bash
python -m pip install -r requirements-test.txt
pytest
```

Tests use the dedicated `server.test_settings` configuration and an in-memory
SQLite test database; no MySQL instance or external service is required.

## Search

Product, customer, and order search is powered by Elasticsearch. Local Docker
Compose starts Elasticsearch automatically and indexes existing records when
the backend starts. Search indices are updated when these records are saved or
deleted.

When deploying outside Compose, configure `ELASTICSEARCH_URL` (and optional
`ELASTICSEARCH_USER` / `ELASTICSEARCH_PASSWORD` credentials), then run
`python manage.py reindex_search` to initialize indices and index existing
records. To recreate all indices, run `python manage.py reindex_search
--rebuild`.


## Installation

Required initial dependencies for this project are as follows;

a) python3

b) pipenv

c) docker


Required files for installation are as follows;

a) .env file (this is scaffolded for you in .env.example. ask the devs to provide the required values for your local computer)


with these files in the root  directory,  from the following commands to install all necessary dependencies and start the backend container


```bash
$ docker compose build
$ docker compose up
```


Development environments and development dependencies

a) docker-compose

Docker-compose  is used to rapidly build and deploy the backend image.  It is installable through pip3 and requires that docker is installed.


pip3 install docker-compose



```sql
mysql# create database pearmonie;

mysql# grant all privileges on pearmonie.* to '<username>'@'localhost' identified by '<password>';

mysql# exit;
```


# using docker-compose
$ docker-compose run server pipenv run python3 manage.py migrate
```


## Deployment

the guitar depository maintains two main branches, main and dev.  Attached to this branches specific workflows that handle deployment  to the various deployment servers. The main branch  is connected to a workflow that specifically deploys the application to the production server. This means that any comment that is pushed to the origin will automatically be acted upon and deployed to the production server. The same goes for the development server which uses the dev branch.


```
main -> production server

dev -> development server
```


these workflows can be found in /.github/workflows/  directory.



## Linting and formatting

the project uses a precommit hook that can be set on the local system. the preferred linter is called Black.
