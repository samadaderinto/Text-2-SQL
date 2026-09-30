# AudQL

This is the Django and Django REST Framework backend for AudQL. It can run
locally through Docker Compose, in test mode with isolated SQLite settings, or
as a production Docker image.

For current living backend documentation, see
[../docs/BACKEND.md](../docs/BACKEND.md). For system-level architecture and
observability, see [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) and
[../docs/OBSERVABILITY.md](../docs/OBSERVABILITY.md). Keep those files updated
whenever backend behavior changes.

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
the backend starts. Search index updates are queued when these records are
saved or deleted.

Repeated Elasticsearch searches and query-plan data retrievals are cached for
300 seconds by default. Product, customer, and order changes invalidate the
corresponding cached results after the database transaction commits. Local
Compose uses Redis through `django-redis`, so the API and worker share the same
cache. Configure `CACHE_LOCATION` with a managed Redis URL in production.
`DATA_CACHE_TIMEOUT` controls the cache lifetime in seconds.

When deploying outside Compose, configure `ELASTICSEARCH_URL` (and optional
`ELASTICSEARCH_USER` / `ELASTICSEARCH_PASSWORD` credentials), then run
`python manage.py reindex_search` to initialize indices and index existing
records. To recreate all indices, run `python manage.py reindex_search
--rebuild`.

## Background jobs

The API queues query generation, audio transcription, email delivery, order
exports, and search-index updates through Kafka. Job records are stored in the
database so the worker can recover pending work if Kafka is temporarily
unavailable. Start the app stack with `docker compose -f compose.yaml up --build`
from the repository root to run the worker alongside the API. Authenticated clients poll `/jobs/<job_id>/` for
completion; order exports can then be downloaded from
`/jobs/<job_id>/download/`. Configure `KAFKA_JOB_TOPIC` and
`KAFKA_JOB_GROUP_ID` to override the local defaults. Audio uploads are stored
until a worker finishes processing them, so multi-instance deployments must
configure a shared Django storage backend for media files.

## Logs and errors

The app stack and monitoring stack are separated:

```bash
docker compose -f compose.yaml up --build
docker compose -f monitoring/compose.yaml up
```

Open Grafana at <http://localhost:3000> (default local login `admin` /
`change-me-local`) and select the **AudQL application logs** dashboard. It
includes log-volume and error trends, newest-first log details, and service,
environment, and severity filters. For ad-hoc searching, use **Explore** and
the provisioned Loki data source; filter by labels such as
`{service="backend", level="error"}` and search message text with
`|= "search phrase"`.

Backend JSON logs go to the console and, in Compose, Kafka. Vector in the
monitoring stack consumes `audql.logs` and ships events to Loki. It also
collects Docker container stdout/stderr through the Docker socket. Frontend
uncaught exceptions, unhandled promise rejections, and API server errors are
sent to a throttled backend endpoint and use the same app-log pipeline. Events
omit request bodies and authentication headers; email addresses and common
credential patterns are redacted. Set `KAFKA_LOGGING_ENABLED=false` to keep
backend logs on the console only, or `VITE_ERROR_REPORTING_ENABLED=false` to
turn off browser reporting. The default Grafana credentials are for local
development only; change them before exposing Grafana outside a trusted
development machine.

The services also run individually if needed: Django API on port 8000, Grafana
on 3000, Loki on 3100, and Kafka on 9092. Keep monitoring services on a trusted
private/local network; do not expose Loki, Vector, exporters, or the
unauthenticated local Kafka broker to the public internet.


## Installation

Required initial dependencies for this project are as follows;

a) python3

b) pipenv

c) docker


Required files for installation are as follows;

a) .env file (this is scaffolded for you in .env.example. ask the devs to provide the required values for your local computer)


with these files in the root directory, run the following commands to install
all necessary dependencies and start the backend container


```bash
$ docker compose -f compose.yaml build
$ docker compose -f compose.yaml up
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

The repository maintains `main` and `dev` branches. Deployment workflows are
attached to those branches and can be found in the `.github/workflows/`
directory.


```
main -> production server

dev -> development server
```


## Linting and formatting

the project uses a precommit hook that can be set on the local system. the preferred linter is called Black.
