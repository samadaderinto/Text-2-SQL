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
`server/.env.example`. Do not add production env files. Render runtime values
are configured in the Render service environment (the `sync: false` entries in
`render.yaml`). GitHub Actions secrets are used only by workflows that require
them, such as deploy hooks and deployment verification.

Core Django settings:

| Variable | Default in Compose | Purpose |
| --- | --- | --- |
| `DEBUG` | `true` | Enables local debug behavior. Use `false` outside development. |
| `SECRET_KEY` | `dev-only-secret-key-change-me` | Django signing key. Must be strong and private in real deployments. |
| `OPENAI_API_KEY` | `dev-placeholder` | Used by query/audio flows that call OpenAI. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,text2sql-server,server` | Comma-separated Django host allowlist; `text2sql-server` is required for internal Compose probes. |
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
| `KAFKA_REQUEST_TIMEOUT_MS` | `15000` | Worker Kafka request timeout; must exceed the broker session timeout. |
| `KAFKA_API_VERSION_AUTO_TIMEOUT_MS` | `5000` | Worker timeout for Kafka API-version negotiation. |
| `CLIENT_LOG_RATE` | `30/min` in `.env.example` | DRF throttle scope for frontend log ingestion. |

Email:

| Variable | Local default | Purpose |
| --- | --- | --- |
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Prints email locally instead of sending. |
| `EMAIL_HOST` | `smtp.resend.com` | Resend SMTP endpoint; used by the production SMTP backend. |
| `EMAIL_PORT` | `465` | SMTP port. Port 465 uses implicit SSL. |
| `EMAIL_USE_TLS` | `false` | Enables STARTTLS when using a STARTTLS port. |
| `EMAIL_USE_SSL` | `true` | Enables implicit SSL for port 465. |
| `EMAIL_HOST_USER` | `resend` | Resend's required SMTP username. |
| `EMAIL_HOST_PASSWORD` | empty | Resend API key; keep it private. |
| `DEFAULT_FROM_EMAIL` | `notifications@example.com` | Sender address; production must use an address on a verified Resend domain. |

Firebase Cloud Messaging (FCM):

| Variable | Local default | Purpose |
| --- | --- | --- |
| `FCM_ENABLED` | `false` | Enables server-side FCM push delivery. |
| `FCM_PROJECT_ID` | empty | Firebase project used by the FCM HTTP API. |
| `FCM_SERVICE_ACCOUNT_FILE` | empty | Path to the server-side service-account JSON file, if using a file. |
| `FCM_SERVICE_ACCOUNT_JSON` | empty | Server-side service-account JSON, if supplied inline instead of as a file. |

The browser Firebase configuration is set through `VITE_FIREBASE_*` variables;
those values initialize the Firebase web SDK and do not replace the private
server service-account credentials. Push delivery uses FCM. Email delivery
uses Resend over SMTP through Django's configured email backend; local
development defaults to the console backend. Configure the Resend API key and
verified sender address on both the Render API and worker services. Email and
push notification preferences are independently respected. The application
has no SMS notification provider.

## Background jobs

The API stores job records in the database and publishes work notifications to
Kafka. The worker consumes notifications, claims and processes the durable job
records, then updates their status. A database recovery scan retries eligible
queued or stale jobs if a broker notification was missed or a worker stopped.
Clients poll job status by ID.

Current job categories include query generation, audio transcription,
email delivery, order exports, and search-index updates. If a new job kind is
added, update this section, serializers, worker handling, tests, and any
frontend polling behavior.

Important operational constraints:

- Run the worker as well as the API in deployments that accept queued work.
- Job state is durable in the relational database; Kafka is the dispatch
  channel, not the only record that work exists.
- Audio files must remain available to the worker. Multi-instance deployments
  need shared media storage.
- Job status and downloadable export endpoints require authentication and
  enforce job ownership.

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
docker network create text-2-sql-app-net
docker compose -f compose.yaml up --build -d
docker compose exec text2sql-server python manage.py reindex_search --rebuild
```

The named network is external and must be created once before starting the
backend, frontend (`client/compose.yaml`), or monitoring Compose stack. The
backend's Compose command applies migrations and initializes the search index
on startup.

To build the backend container image without starting:

```bash
docker compose -f compose.yaml build
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
