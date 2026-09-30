# Architecture

This document is the high-level map for AudQL. Update it when service
boundaries, data flow, infrastructure, or major runtime behavior changes.

## Runtime Services

The application runtime is defined in [../compose.yaml](../compose.yaml).

- `client`: React + TypeScript + Vite app. It runs on port `4174` in local
  Compose and talks to the browser-visible backend origin through
  `VITE_API_BASE_URL`.
- `server`: Django + Django REST Framework API. It runs on port `8000`,
  applies migrations at startup in Compose, rebuilds search indexes, exposes
  OpenAPI docs, health checks, logs, and Prometheus metrics.
- `worker`: Django management command process that consumes Kafka-backed jobs.
  It handles long-running work such as query generation, audio transcription,
  email delivery, exports, and search-index updates.
- `database`: MySQL 8.4 for local persistence.
- `redis`: shared server-side Django cache for API and worker processes.
- `elasticsearch`: single-node Elasticsearch used for product, customer, and
  order search.
- `kafka`: Redpanda Kafka-compatible broker for application jobs and log
  events.

Monitoring is defined separately in
[../monitoring/compose.yaml](../monitoring/compose.yaml).

- `vector`: consumes structured log events from Kafka and ships them to Loki.
- `loki`: log storage queried by Grafana.
- `prometheus`: metrics and probe storage.
- `grafana`: dashboards for logs, application metrics, service health, and
  infrastructure metrics.

## Tooling inventory

Application tools:

- Django 4 + Django REST Framework: backend API, auth, serializers, routing,
  permissions, and testable service boundaries.
- SimpleJWT: access and refresh token authentication.
- drf-spectacular: OpenAPI schema and Swagger/Redoc docs.
- MySQL 8.4: local relational database.
- Redis 7: shared server-side cache.
- Elasticsearch 9: indexed search for products, customers, and orders.
- Redpanda: Kafka-compatible local broker for jobs and logs.
- React 18 + TypeScript + Vite: frontend runtime and development server.
- Axios: typed API client behavior, JWT attachment, refresh retry, and 5xx
  reporting.
- React Toastify: centralized frontend notifications.
- Vitest + React Testing Library: frontend unit/component tests.
- pytest: backend unit/API tests.

Observability tools:

- Prometheus: metrics scraping and short local retention.
- Grafana: dashboards and exploratory views for Prometheus and Loki data.
- Loki: local log storage.
- Vector: Kafka-to-Loki log shipper.
- Blackbox exporter: HTTP probes for frontend and backend health endpoints.
- Kafka exporter: Redpanda/Kafka metrics and consumer lag.
- MySQL exporter: database availability and runtime metrics.
- Redis exporter: cache availability and runtime metrics.
- Elasticsearch exporter: cluster, node, and index metrics.
- cAdvisor: container CPU and memory metrics.

## Request flow

1. Compose publishes the `client` container at `http://localhost:4174` and the
   `server` container at `http://localhost:8001`.
2. The browser renders the React app and uses the Axios API client in
   `client/src/utils/api.ts` to call the backend origin.
3. Authenticated requests include a decrypted JWT access token in the
   `Authorization` header.
4. Django routes API calls through DRF viewsets in `server/app/views.py`.
5. Business logic lives in service classes in `server/app/services.py`.
6. Persistent data is stored through Django models in `server/app/models.py`.
7. Expensive or asynchronous work is queued through `server/app/job_queue.py`
   and processed by `run_queue_worker`.
8. The frontend polls `/jobs/<job_id>/` when an API action returns a queued job.

## Text-to-SQL flow

The query feature accepts typed prompts and audio prompts. The backend builds a
structured query plan instead of trusting raw SQL text directly. Query-plan
generation, audio transcription, and execution are pushed through the job queue
when work may take longer than a normal request-response cycle.

Search and query-planning helpers cache repeated reads for a short period. Model
save/delete hooks invalidate relevant cache and search data after database
transactions commit.

## Observability flow

- Django metrics are emitted by `app.metrics.MetricsMiddleware` and exposed at
  `/metrics/`.
- Liveness is exposed at `/health/live/`; readiness is exposed at `/health/`.
- Backend logs are structured JSON events and can also be published to Kafka.
- Frontend uncaught errors, unhandled rejections, and server-side API failures
  are sent to `/logs/client/`.
- Vector consumes log events from Kafka and writes them to Loki using stable
  service, environment, and level labels; container logs are normalized before
  storage as well.
- Prometheus scrapes Django, Kafka exporter, MySQL exporter, Redis exporter,
  Elasticsearch exporter, cAdvisor, blackbox probes, and itself.
- Grafana provisions Prometheus and Loki datasources plus AudQL dashboards.

## Configuration principles

Local Compose reads only the app-owned local env files:

- `server/.env`
- `client/.env`

Only their examples are committed:

- `server/.env.example`
- `client/.env.example`

Do not add root `.env` files, production env files, or special env files in
other directories. Production-like deployments must get secrets from GitHub
Actions secrets and the deployment provider's secret/env-var store.

Local defaults are intentionally development-only. Production deployments must
provide strong secrets, explicit host allowlists, external storage for uploaded
media when multiple app instances exist, durable databases, and protected
observability endpoints.

## Local ports

Application stack:

| Port | Service | Purpose |
| --- | --- | --- |
| `4174` | `client` | Vite frontend |
| `8000` | `server` | Django API and OpenAPI docs |
| `3306` | `database` | MySQL |
| `6379` | `redis` | Redis cache |
| `9200` | `elasticsearch` | Elasticsearch HTTP API |
| `9092` | `kafka` | local Kafka-compatible broker |

Monitoring stack:

| Port | Service | Purpose |
| --- | --- | --- |
| `3000` | `grafana` | dashboards |
| `9091` | `prometheus` | metrics UI/API |
| `3100` | `loki` | log query API |
| `9308` | `kafka-exporter` | Kafka metrics |
| `9104` | `mysql-exporter` | MySQL metrics |
| `9121` | `redis-exporter` | Redis metrics |
| `9114` | `elasticsearch-exporter` | Elasticsearch metrics |
| `8080` | `cadvisor` | container metrics |
| `9115` | `blackbox-exporter` | HTTP probe metrics |

Except for the app-facing ports, observability ports are bound to `127.0.0.1`
in Compose so they are available locally without being exposed on every network
interface.

## Persistent volumes

| Volume | Used by | Contents |
| --- | --- | --- |
| `client_node_modules` | `client` | container-local frontend dependencies |
| `mysql_data` | `database` | MySQL data directory |
| `redis_data` | `redis` | Redis append-only cache data |
| `elasticsearch_data` | `elasticsearch` | Elasticsearch data directory |
| `kafka_data` | `kafka` | Redpanda/Kafka log data |
| `loki_data` | `loki` | Loki chunks, indexes, and compactor data |
| `grafana_data` | `grafana` | Grafana database, sessions, local state |
| `prometheus_data` | `prometheus` | Prometheus TSDB data |
