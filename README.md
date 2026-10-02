# AudQL

AudQL is a text-to-SQL application with a React/Vite frontend, a Django REST
backend, MySQL persistence, Elasticsearch search, Kafka-backed background jobs,
and a local observability stack built around Prometheus, Loki, Vector, and
Grafana.

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

Create the two local environment files from their templates:

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Edit those files for local values. They are ignored by Git; do not create a
root-level or production environment file. Without a real `OPENAI_API_KEY`, the
app starts, but query or audio workflows that call OpenAI will fail.

```bash
docker compose -f compose.yaml up --build
```

Compose runs the React/Vite frontend, Django API, Kafka-backed worker, MySQL,
Redis cache, Elasticsearch, and Redpanda (Kafka-compatible broker). The backend
waits for its dependencies, applies database migrations, and initializes the
search index before serving requests; the frontend waits for backend
readiness.

| Local URL | Service |
| --- | --- |
| <http://localhost:4174> | Frontend |
| <http://localhost:8001> | Backend API |
| <http://localhost:8001/docs/swagger/> | OpenAPI / Swagger |
| <http://localhost:8001/health/> | Backend readiness |
| <http://localhost:8001/health/live/> | Backend liveness |

The browser-facing API origin is configured by `VITE_API_BASE_URL` in
`client/.env`. Compose stores MySQL, Redis, Elasticsearch, and Kafka data in
named volumes, which persist across container recreation. Compose credentials
and local Grafana defaults are development-only; never use them with
non-development data.

To inspect service health or rebuild search indices:

```bash
docker compose ps
docker compose exec text2sql-server python manage.py reindex_search --rebuild
```

Run backend tests with an isolated in-memory SQLite database; tests do not
connect to or modify the Compose database:

```bash
cd server
python -m pip install -r requirements-test.txt
pytest
```

For frontend tests and a production build:

```bash
cd client
npm test
npm run build
```

## Monitoring

Monitoring is a separate Compose stack. Start the app first so monitoring
services can join its Docker network:

```bash
docker compose -f monitoring/compose.yaml up
```

See [Observability](docs/OBSERVABILITY.md) for service ports, Grafana
dashboards, log queries, and troubleshooting.

## Deployment

`render.yaml` defines the Render API, worker, frontend, and PostgreSQL
resources. Local Compose uses MySQL; the Render database is a free trial that
expires after 30 days and is not suitable for data that must be retained.
Production runtime secrets belong in the deployment provider's secret store;
GitHub Actions secrets are used for workflow-only values such as deploy hooks.

The `Deploy to Render` workflow runs after successful tests on pushes to
`main`. The `Production incident monitor` workflow probes the configured
production readiness URL every five minutes and opens a tracked issue after
repeated failures, closing it after recovery. See the workflow files under
`.github/workflows/` for required Actions secrets and exact behavior.
