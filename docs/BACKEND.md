# Backend

The backend is a Django and Django REST Framework application in `server/`.
Update this document when backend modules, API behavior, job kinds, settings,
or operational behavior changes.

## Important modules

- `server/server/settings.py`: Django settings, database selection, CORS/CSRF,
  REST framework defaults, cache, search, logging, and observability settings.
- `server/server/urls.py`: top-level routes for health, metrics, client logs,
  jobs, OpenAPI docs, admin, and app viewsets.
- `server/app/urls.py`: DRF router registration for auth, query, customers,
  products, orders, and settings.
- `server/app/views.py`: request parsing and API endpoints.
- `server/app/services.py`: domain and integration logic.
- `server/app/serializers.py`: request and response validation.
- `server/app/models.py`: users, store data, products, customers, orders,
  query records, and queued jobs.
- `server/app/job_queue.py`: job persistence and Kafka enqueue behavior.
- `server/app/management/commands/run_queue_worker.py`: background worker loop.
- `server/app/search_index.py`: Elasticsearch indexing and search helpers.
- `server/app/metrics.py`: Prometheus request metrics and `/metrics/` response.
- `server/app/health.py`: liveness and readiness checks.
- `server/app/observability.py`: frontend/client log ingestion.

## API surface

Top-level routes:

- `GET /health/live/`: process liveness. Does not check dependencies.
- `GET /health/`: readiness. Checks database, cache, and Elasticsearch when
  enabled.
- `GET /metrics/`: Prometheus metrics.
- `POST /logs/client/`: throttled frontend error reporting endpoint.
- `GET /jobs/<job_id>/`: queued job status.
- `GET /jobs/<job_id>/download/`: downloadable export results.
- `GET /docs/`, `/docs/swagger/`, `/docs/redoc/`: OpenAPI schema and docs.

Router-backed resources:

- `/auth/`: signup, login, logout, token refresh, activation, password reset.
- `/query/`: text-to-SQL and audio query workflows.
- `/customers/`: customer CRUD and search.
- `/product/`: product CRUD and search.
- `/orders/`: order CRUD, search, and export jobs.
- `/settings/`: account/store settings and notification preferences.

Authentication defaults to JWT through DRF settings. Most API endpoints require
an authenticated user unless explicitly marked public.

## Data and search

Local Compose uses MySQL. Tests use isolated SQLite settings through
`server/server/test_settings.py`.

Search is backed by Elasticsearch. Product, customer, and order writes enqueue
index maintenance work after database transactions commit. Search results are
scoped to the authenticated owner.

The default runtime cache is Redis through `django-redis`, controlled by
`CACHE_BACKEND`, `CACHE_LOCATION`, `CACHE_KEY_PREFIX`,
`CACHE_IGNORE_EXCEPTIONS`, and `DATA_CACHE_TIMEOUT`. Tests override this to
Django `LocMemCache` so the unit suite does not require Redis.

## Configuration

Local backend config lives in `server/.env`; the committed template is
`server/.env.example`. Do not add production env files. Production values are
provided through GitHub Actions secrets and the deployment provider.

Core Django settings:

| Variable | Default in Compose | Purpose |
| --- | --- | --- |
| `DEBUG` | `true` | Enables local debug behavior. Use `false` outside development. |
| `SECRET_KEY` | `dev-only-secret-key-change-me` | Django signing key. Must be strong and private in real deployments. |
| `OPENAI_API_KEY` | `dev-placeholder` | Used by query/audio flows that call OpenAI. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated Django host allowlist. |
| `FRONTEND_URL` | `http://localhost:4174` | Used for redirects, CORS, and CSRF trusted origins. |
| `DEPLOY_ENV` | `local` | Environment label used in logs and dashboards. |

Database and cache:

| Variable | Default in Compose | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | unset | Optional single database URL. Takes precedence when set. |
| `MYSQL_DATABASE` | `text2sql_db` | MySQL image database name for Compose. |
| `MYSQL_NAME` | `text2sql_db` | MySQL database name. |
| `MYSQL_USER` | `text2sql_user` | MySQL application user. |
| `MYSQL_PASSWORD` | `dev-only-db-password-change-me` | MySQL application password. |
| `MYSQL_HOST` | `database` | Compose service name for MySQL. |
| `MYSQL_PORT` | `3306` | MySQL port. |
| `CACHE_BACKEND` | `django_redis.cache.RedisCache` | Django cache backend. |
| `CACHE_LOCATION` | `redis://redis:6379/1` | Redis URL/database used by Django cache. |
| `CACHE_KEY_PREFIX` | `audql` | Prefix applied to cache keys. |
| `CACHE_IGNORE_EXCEPTIONS` | `false` | Whether Redis errors should be swallowed by the cache backend. |
| `DATA_CACHE_TIMEOUT` | `300` | Cache lifetime in seconds for repeated reads. |

Search, queue, and logs:

| Variable | Default in Compose | Purpose |
| --- | --- | --- |
| `ELASTICSEARCH_URL` | `http://elasticsearch:9200` | Search cluster URL. |
| `ELASTICSEARCH_HOST` | `elasticsearch` | Host used to build the default URL. |
| `ELASTICSEARCH_PORT` | `9200` | Port used to build the default URL. |
| `ELASTICSEARCH_USER` | unset | Optional Elasticsearch username. |
| `ELASTICSEARCH_PASSWORD` | unset | Optional Elasticsearch password. |
| `ELASTICSEARCH_ENABLED` | `true` in `.env.example` | Enables readiness and search integration checks. |
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Broker list used by API and worker. |
| `KAFKA_JOB_TOPIC` | `audql.jobs` | Background job topic. |
| `KAFKA_JOB_GROUP_ID` | `audql-workers` | Worker consumer group. |
| `KAFKA_LOG_TOPIC` | `audql.logs` | Structured log topic consumed by Vector. |
| `KAFKA_LOGGING_ENABLED` | `true` | Enables publishing backend logs to Kafka. |
| `CLIENT_LOG_RATE` | `30/min` in `.env.example` | DRF throttle scope for frontend log ingestion. |

Email:

| Variable | Local default | Purpose |
| --- | --- | --- |
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Prints email locally instead of sending. |
| `EMAIL_HOST` | empty/example | SMTP host for real delivery. |
| `EMAIL_PORT` | empty/`465` example | SMTP port. |
| `EMAIL_HOST_USER` | empty/example | SMTP username and default from address. |
| `EMAIL_HOST_PASSWORD` | empty/example | SMTP password. |

## Background jobs

The API stores job records in the database and publishes work to Kafka. The
worker consumes jobs and updates their status. Clients poll job status by ID.

Current job categories include query generation, audio transcription,
email delivery, order exports, and search-index updates. If a new job kind is
added, update this section, serializers, worker handling, tests, and any
frontend polling behavior.

## Metrics and health

`MetricsMiddleware` records:

- `audql_http_requests_total`
- `audql_http_request_duration_seconds`
- `audql_http_errors_total`

Readiness failures log which dependency failed while keeping connection details
out of the HTTP response.

## Local commands

```bash
cd server
python -m pip install -r requirements-test.txt
pytest
```

With Compose:

```bash
docker compose -f compose.yaml up --build
docker compose exec server python manage.py reindex_search --rebuild
```

## Backend documentation checklist

When backend code changes, update this file if the change affects:

- endpoints or request/response shapes
- authentication or permission behavior
- environment variables or settings
- models, migrations, or ownership rules
- job kinds or worker behavior
- health checks, metrics, logs, or dashboards
- external integrations such as OpenAI, Kafka, Elasticsearch, or email
