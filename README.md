# AudQL

AudQL is a web application for managing store data and querying it with natural
language. It has a React/TypeScript frontend, a Django REST API, relational
storage, Elasticsearch search, Redis caching, and Kafka-dispatched background
jobs. Local observability is provided by Prometheus, Loki, Vector, and Grafana.

## What the application does

- Account signup, email activation, login, password reset, and account settings.
- Text and audio query workflows, including asynchronous query processing.
- Product, customer, and order management, search, and order export.
- Queued email delivery and Firebase Cloud Messaging (FCM) push notifications.
  FCM is used for push delivery; queued email uses Resend's SMTP service via
  Django's email backend. The application does not send SMS.
- Browser/API error reporting, backend metrics, health checks, and local
  dashboards.

## How the pieces fit together

The relational database is the durable source of application records and job
state. Elasticsearch is a derived search index; Redis is used for cache data;
and Kafka transports job notifications to the worker. The worker also scans
the database for queued or stale jobs, so pending work can be recovered when
Kafka is unavailable. Search/index updates and exports are processed outside
the web request path.

```text
Browser -> React/Vite -> Django REST API -> relational database
                              |              |-- Redis cache
                              |              |-- Elasticsearch search index
                              |              `-- Kafka -> queue worker
                              |                          |-- email backend
                              |                          |-- FCM push
                              |                          `-- exports / query jobs
                              `-- /metrics/ and /health/ -> monitoring stack
```

The dedicated `server/compose.yaml` defines the backend application and data stack (`text-2-sql-app`).
The dedicated `client/compose.yaml` defines the frontend stack (`text-2-sql-frontend`),
and `monitoring/compose.yaml` defines local dashboards and exporters (`text-2-sql-monitoring`).
All stacks communicate over the shared external Docker network `text-2-sql-app-net`.
Compose uses MySQL locally, while the Render deployment manifest provisions PostgreSQL.
Database-specific differences are handled by Django; tests use isolated
SQLite settings.

## Codebase map

| Path | Responsibility |
| --- | --- |
| `client/compose.yaml` | Dedicated frontend Docker Compose stack. |
| `client/src/components/` | Main signed-in screens and account forms. |
| `client/src/contexts/` | Authentication and store state shared between screens. |
| `client/src/utils/api.ts` | API requests, JWT refresh, and API error handling. |
| `client/src/utils/queue-jobs.ts` | Shared client-side polling for asynchronous jobs. |
| `client/src/utils/push-notifications.ts` | Browser Firebase Messaging setup and device registration. |
| `monitoring/compose.yaml` | Observability and exporter Docker Compose stack. |
| `server/compose.yaml` | Backend API and core infrastructure Docker Compose stack. |
| `server/server/` | Django settings, root URL configuration, and WSGI/ASGI entry points. |
| `server/app/views.py` | HTTP endpoints and DRF viewsets. |
| `server/app/services.py` | Domain workflows and external service integration. |
| `server/app/models.py` | Relational domain records, notification devices, and queue jobs. |
| `server/app/job_queue.py` | Durable job creation, dispatch, and processing. |
| `server/app/management/commands/run_queue_worker.py` | Kafka consumer and database recovery scan. |
| `server/app/search_index.py`, `server/app/data_cache.py` | Elasticsearch integration and data-cache keys/invalidation. |
| `server/app/tests.py` and `server/app/test_*.py` | Backend unit and API integration tests. |
| `observability/` | Prometheus, Vector, Loki, and Grafana configuration. |
| `.github/workflows/` | CI, security checks, deployment triggers, and production health monitoring. |

## Documentation

- [Backend](docs/BACKEND.md): Django API, data/search, cache, configuration,
  background jobs, and backend checks.
- [Frontend](docs/FRONTEND.md): React app, API client, user interface, and
  frontend checks.
- [Observability](docs/OBSERVABILITY.md): logs, metrics, dashboards, probes,
  exporters, and monitoring setup.
- [Documentation maintenance](docs/DOCUMENTATION.md): which guide to update
  when behavior changes.

The system overview and local setup are kept here; implementation details live
in the relevant backend, frontend, or observability guide rather than in a
separate architecture or containerization document.

## Local development

Prerequisites: Docker Engine/Desktop with the Compose plugin. Create the two
local environment files from their templates:

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Edit those files for local values. They are ignored by Git; do not create a
root-level or production environment file. Without a real `OPENAI_API_KEY`, the
app starts, but query or audio workflows that call OpenAI will fail.

The Compose files use a pre-existing external Docker network; create it once before
starting the stacks:

```bash
docker network create text-2-sql-app-net
```

To bring up both the backend and frontend stacks together:

```bash
docker compose -f server/compose.yaml up --build -d
docker compose -f client/compose.yaml up --build -d
```

To bring up individual stacks:

```bash
# Bring up backend API and data stack only
docker compose -f server/compose.yaml up --build -d

# Bring up frontend stack only
docker compose -f client/compose.yaml up
# Or build and start in background:
docker compose -f client/compose.yaml up --build -d
```

The backend stack runs the Django API, Kafka-backed worker, MySQL, Redis cache,
Elasticsearch, and Redpanda (Kafka-compatible broker). The backend waits for its
dependencies, applies database migrations, and initializes the search index before
serving requests. The frontend stack builds and runs the React/Vite development server.

To build the container images for both stacks without starting them:

```bash
docker compose -f server/compose.yaml build
docker compose -f client/compose.yaml build
```

| Local URL | Service |
| --- | --- |
| <http://localhost:4174> | Frontend |
| <http://localhost:8001> | Backend API |
| <http://localhost:8001/docs/swagger/> | OpenAPI / Swagger |
| <http://localhost:8001/health/> | Backend readiness |
| <http://localhost:8001/health/live/> | Backend liveness |
| <http://localhost:8001/admin/> | Django admin (shared admin credentials) |

The browser-facing API origin is configured by `VITE_API_BASE_URL` in
`client/.env`. Compose stores MySQL, Redis, Elasticsearch, and Kafka data in
named volumes, which persist across container recreation. Compose credentials
and local Grafana defaults are development-only; never use them with
non-development data.

To inspect service health or rebuild search indices:

```bash
docker compose -f server/compose.yaml ps
docker compose -f client/compose.yaml ps
docker compose -f server/compose.yaml exec text2sql-server python manage.py reindex_search --rebuild
```

To stop the application stacks without removing their persistent named volumes:

```bash
docker compose -f client/compose.yaml down
docker compose -f server/compose.yaml down
```

### Standalone backend development and tests

Run backend tests with an isolated in-memory SQLite database (no Compose services required):

```bash
cd server
python -m pip install -r requirements-test.txt
pytest
```

To run the Django server directly on the host:

```bash
cd server
python manage.py runserver 0.0.0.0:8001
```

### Standalone frontend development and build

Run the Vite development server directly on the host:

```bash
cd client
npm install
npm run dev
```

Run frontend unit and integration tests (Vitest, jsdom, React Testing Library):

```bash
cd client
npm test
```

Create a production build of the frontend:

```bash
cd client
npm run build
```

`npm run build` runs `tsc -b` for TypeScript project checking and Vite for production asset bundling into `client/dist/`. To build the frontend container image directly with Docker:

```bash
docker compose -f client/compose.yaml build
# or:
docker build -t text2sql-frontend -f client/Dockerfile client
```

## Monitoring

Monitoring is a separate Compose stack. Start the app first so monitoring
services can join its Docker network:

```bash
docker compose -f monitoring/compose.yaml up
```

Sign in to Grafana at <http://localhost:3000> with the same `ADMIN_EMAIL` and
`ADMIN_PASSWORD` configured for Django. The Render Blueprint also defines a
Grafana service whose initial admin login is sourced directly from the API
service's production variables. Its dashboards are provisioned from this
repository on each deploy; the service intentionally does not persist ad-hoc
UI changes, so credential changes take effect on the next deployment.

See [Observability](docs/OBSERVABILITY.md) for service ports, Grafana
dashboards, log queries, and troubleshooting.

## Configuration and secrets

Use only the checked-in templates as the source of local configuration:

- `server/.env.example` -> `server/.env` for API, worker, and local
  infrastructure settings.
- `client/.env.example` -> `client/.env` for Vite and Firebase web-client
  settings.

Never commit local `.env` files, private Firebase service-account credentials,
database credentials, or API keys. The Render manifest (`render.yaml`) declares
production runtime variables for its services; values marked `sync: false`
must be configured in Render. GitHub Actions secrets are for workflow
operations (deploy hooks and the production health-check URL) and selected
deployment verification values, not a replacement for the service runtime
environment. See [Backend configuration](docs/BACKEND.md#configuration) and
[Frontend configuration](docs/FRONTEND.md#configuration) for variable details.

## Deployment

`render.yaml` defines the Render API, worker, frontend, and PostgreSQL
resources. Local Compose uses MySQL; Render provisions PostgreSQL. Confirm
Render database plan, retention, and backup terms before using it for
production data. Runtime secrets belong in Render's service environment.

The `Tests` workflow runs frontend tests/build and backend tests for pull
requests and pushes to `main` and `dev`. The `Deploy to Render` workflow deploys
the frontend and backend after a successful `main` push test run, using
`RENDER_BACKEND_DEPLOY_HOOK` and `RENDER_FRONTEND_DEPLOY_HOOK`. It also checks
that `PRODUCTION_SECRET_KEY`, `OPENAI_API_KEY`, and
`PRODUCTION_CACHE_LOCATION` Actions secrets are set for deployment
verification/mirroring. The `Production incident monitor` workflow runs every
five minutes and requires `PRODUCTION_HEALTHCHECK_URL`; it records repeated
readiness failures as an issue and closes the incident after recovery. Read the
workflow files under `.github/workflows/` for exact behavior.

## Design decisions and boundaries

- Keep request/response APIs in Django REST Framework; generated OpenAPI docs
  are available at `/docs/swagger/`.
- Keep potentially slow or retryable work in persisted queue jobs, dispatched
  through Kafka and executed by the separate worker.
- Treat the database as durable state. Elasticsearch and Redis are supporting
  systems, not sources of truth.
- Use resource ownership checks for store data; search and list results must
  remain scoped to the authenticated owner.
- Keep backend application, frontend, and monitoring Compose stacks separate so each stack can be built, developed, and maintained independently.
- Keep local settings in the two package-level `.env` files and provide
  production runtime configuration through Render. CI/deploy workflow secrets
  remain scoped to the workflow that consumes them.

## Further reading

Start with [Backend](docs/BACKEND.md) for API routes, models, jobs, cache, and
server settings; [Frontend](docs/FRONTEND.md) for React routes, auth, API
handling, and client configuration; [Observability](docs/OBSERVABILITY.md) for
metrics/logging and dashboards; and [Documentation maintenance](docs/DOCUMENTATION.md)
for where future changes should be documented.
