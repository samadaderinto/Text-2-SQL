# Containerized Development

For the broader living system docs, see [README.md](README.md),
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and
[docs/OBSERVABILITY.md](docs/OBSERVABILITY.md). Keep this file updated whenever
Compose services, ports, startup behavior, or environment handling changes.

The application stack is defined in [compose.yaml](compose.yaml).

| App service | Purpose | Default host port |
| --- | --- | --- |
| `text2sql-server` | Django development API, built from `server/Dockerfile` | `8001` (container: `8000`) |
| `worker` | Django queue worker for Kafka-backed jobs | Internal |
| `client` | Vite/React dev server | `4174` |
| `database` | MySQL 8.4 database | `3306` |
| `redis` | Redis 7.4 shared Django cache | `6379` |
| `elasticsearch` | Elasticsearch 9 search engine | `9200` |
| `kafka` | Redpanda Kafka-compatible broker | `9092` |

The API waits for MySQL, Redis, Elasticsearch, and Kafka to be healthy. The
frontend waits for the API readiness check before starting. Database, Redis,
Elasticsearch, Kafka, and frontend dependencies use persistent volumes.

Monitoring is defined separately in
[monitoring/compose.yaml](monitoring/compose.yaml).

| Monitoring service | Purpose | Host port |
| --- | --- | --- |
| `grafana` | Dashboards | `3000` |
| `prometheus` | Metrics and probes | `9091` |
| `loki` | Log storage | `3100` |
| `vector` | Collects Kafka app logs and Docker container logs | Internal |
| `kafka-exporter` | Kafka/Redpanda metrics | `9308` |
| `mysql-exporter` | MySQL metrics | `9104` |
| `redis-exporter` | Redis metrics | `9121` |
| `elasticsearch-exporter` | Elasticsearch metrics | `9114` |
| `cadvisor` | Docker container resource metrics | `8080` |
| `blackbox-exporter` | HTTP health probes | `9115` |

## Run

```bash
docker compose -f compose.yaml up --build
```

Then open:

- Frontend: http://localhost:4174
- Backend: http://localhost:8001

To start monitoring as a separate stack attached to the same named Docker
network (`text-2-sql-app-net`):

```bash
docker compose -f monitoring/compose.yaml up
```

To start both stacks detached from the repository root:

```bash
docker compose -f compose.yaml up --build -d
docker compose -f monitoring/compose.yaml up -d
```

## Health checks

The backend exposes two probes:

- `GET /health/live/` confirms that Django is responding and does not depend on
  external services.
- `GET /health/` checks database connectivity, cache read/write access, and
  Elasticsearch when search is enabled. It returns HTTP 503 if a required
  check fails; the response names failing services without exposing connection
  details.

Compose uses the readiness endpoint for the backend container health status,
and waits for it before starting the frontend. Check service health with:

```bash
docker compose ps
curl -i http://localhost:8001/health/
curl -i http://localhost:8001/health/live/
```

## Environment

Local environment values live in exactly two ignored files:

- `server/.env`
- `client/.env`

Their committed templates are:

- `server/.env.example`
- `client/.env.example`

For local development, copy the examples and edit the local files:

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
docker compose -f compose.yaml up --build
```

Without `OPENAI_API_KEY`, the app will still boot, but voice-to-SQL requests that call OpenAI will fail.

Do not create root-level env files or per-directory special Compose env files.
Production values should come from GitHub Actions secrets and the deployment
provider's secret/env-var store, not committed files.

In Compose, Django waits for both MySQL and Elasticsearch health checks, applies
migrations, then runs `reindex_search` before starting. Elasticsearch indexes
products, customers, and orders, and model saves/deletes keep those indexes
up to date. Search requests are scoped to the authenticated owner; an
unavailable Elasticsearch service returns HTTP 503 rather than silently
falling back to database scans.

MySQL data is stored in `mysql_data` and Elasticsearch data in
`elasticsearch_data`; both survive container recreation. The Compose
credentials are for local development only; set strong values before using
the stack with non-development data.

The test settings always use an isolated in-memory SQLite database. Running the
test suite does not connect to or modify the Compose MySQL database.

To rebuild search indices and repopulate them from the database:

```bash
docker compose exec text2sql-server python manage.py reindex_search --rebuild
```

The default app stack starts Elasticsearch. For deployments outside Compose,
set `ELASTICSEARCH_URL` (and `ELASTICSEARCH_USER` /
`ELASTICSEARCH_PASSWORD` when authentication is enabled), then run
`python manage.py reindex_search` after initial deployment.

The server image does not install `ffmpeg`. The current backend sends recorded WebM files directly to OpenAI, so local transcoding is not needed for normal development. Add `ffmpeg` back to `server/Dockerfile` only if the backend starts converting audio locally.

## Notes

- Compose applies migrations before starting Django's dev server. The Render
  container applies migrations and collects static files before starting
  Gunicorn.
- SQLite files and `.env` files are excluded from image build contexts.
- The frontend talks to `http://localhost:8001` by default through `VITE_API_BASE_URL`.

## Render deployment

`render.yaml` defines a Dockerized Django API, a static React frontend, and a
Render-managed PostgreSQL database. Local Compose continues to use MySQL.
The PostgreSQL database uses Render's free trial plan and expires 30 days
after creation; do not use it for data that must be retained.

The `Deploy to Render` GitHub Actions workflow runs only after the `Tests`
workflow succeeds for a push to `main`. After creating the Blueprint in Render,
add these repository Actions secrets using each service's deploy hook URL:

- `RENDER_BACKEND_DEPLOY_HOOK`
- `RENDER_FRONTEND_DEPLOY_HOOK`

The Blueprint generates Django's `SECRET_KEY` and prompts for `OPENAI_API_KEY`
during initial setup. Configure email-provider credentials and Elasticsearch
if those features are needed.

## Incident response

The `Tests` workflow adds a failure summary to the workflow run and comments on
the pull request when either frontend or backend checks fail. If a later run
passes both checks, the workflow updates its PR comment to show recovery.
Pull requests from forks may not permit write access for the GitHub token; the
workflow run summary remains available in that case.

The `Production incident monitor` workflow checks the production API readiness
endpoint every five minutes. It probes up to five times, 15 seconds apart, and
opens one tracked GitHub issue after three consecutive failures. When readiness
recovers, the workflow closes the issue.

Configure these repository Actions secrets before enabling the monitor:

- `PRODUCTION_HEALTHCHECK_URL`: the production API URL ending in `/health/`

Scheduled workflows run from the repository's default branch.
