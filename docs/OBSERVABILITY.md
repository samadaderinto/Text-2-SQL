# Observability

AudQL monitoring is defined separately in
[../monitoring/compose.yaml](../monitoring/compose.yaml). It attaches to the
same named Docker network as the app stack, so Prometheus, exporters, and
Vector can reach `server`, `database`, `kafka`, and `elasticsearch` by service
name. Update this document whenever observability services, labels, metrics,
dashboards, or alerting behavior changes.

Before starting either Compose file for the first time, create the external
network once from the repository root:

```bash
docker network create text-2-sql-app-net
```

Monitoring is optional and can be omitted when you only need the application.
The exporter stack can use significant laptop resources; stop it when not
needed with `docker compose -f monitoring/compose.yaml down`.

Start the app and frontend stacks first, then monitoring:

```bash
docker compose -f server/compose.yaml up --build -d
docker compose -f client/compose.yaml up --build -d
docker compose -f monitoring/compose.yaml up -d
```

## Monitoring services

| Monitoring service | Purpose | Host port |
| --- | --- | --- |
| `grafana` | Dashboards | `3000` |
| `prometheus` | Metrics and probes | `9091` |
| `loki` | Log storage | `3100` |
| `vector` | Ingests Kafka app logs, direct HTTP frontend logs, and Docker container logs | `8686` |
| `kafka-exporter` | Kafka/Redpanda metrics | `9308` |
| `mysql-exporter` | MySQL metrics | `9104` |
| `redis-exporter` | Redis metrics | `9121` |
| `elasticsearch-exporter` | Elasticsearch metrics | `9114` |
| `cadvisor` | Docker container resource metrics | `8080` |
| `blackbox-exporter` | HTTP health probes | `9115` |

Grafana in local Compose enables anonymous admin access by default (automatically
logged in as Admin when opening http://localhost:3000). On startup, the container
also automatically synchronizes the admin password in `grafana.db` to match the
`ADMIN_PASSWORD` and `ADMIN_EMAIL` configured in `server/.env` for explicit logins.

## App services observed

| App service | Signal collected |
| --- | --- |
| `server` | Prometheus `/metrics/`, health probes, structured app logs, container logs |
| `worker` | Container logs |
| `client` | Health probe, container logs (via Docker socket), and direct client telemetry (via Vector HTTP) |
| `database` | MySQL exporter metrics and container logs |
| `redis` | Redis exporter metrics, container logs, and app readiness/cache behavior |
| `elasticsearch` | Elasticsearch exporter metrics and container logs |
| `kafka` | Kafka exporter metrics and container logs |

## Added tools and what they do

| Tool | Compose service | Config file | What it adds |
| --- | --- | --- | --- |
| Grafana | `grafana` | `observability/grafana/provisioning/` | Dashboards for logs, metrics, health, and infrastructure. |
| Prometheus | `prometheus` | `observability/prometheus.yml` | Metrics scraping, local 7-day TSDB retention, query UI. |
| Loki | `loki` | `observability/loki-config.yaml` | Local log storage with 168-hour retention. |
| Vector | `vector` | `observability/vector.yaml` | Consumes JSON backend events from Kafka, browser/client error events via direct HTTP on :8686, and Docker container stdout/stderr, routing all logs to Loki. |
| Blackbox exporter | `blackbox-exporter` | `observability/blackbox.yml` | Probes HTTP endpoints and emits uptime/duration metrics. |
| Kafka exporter | `kafka-exporter` | Compose command flags | Emits Kafka topic, partition, broker, and consumer lag metrics. |
| MySQL exporter | `mysql-exporter` | `DATA_SOURCE_NAME` env var | Emits MySQL availability and server status metrics. |
| Redis exporter | `redis-exporter` | Compose command flags | Emits Redis availability, memory, keyspace, and command metrics. |
| Elasticsearch exporter | `elasticsearch-exporter` | Compose command flags | Emits Elasticsearch cluster, node, and index metrics. |
| cAdvisor | `cadvisor` | Compose volume mounts | Emits container CPU, memory, and runtime metrics. |

## Logs

Backend logs are structured JSON events. In Compose, backend log events can be
published to Kafka topic `audql.logs`. Vector consumes that topic and writes to
Loki.

Frontend uncaught exceptions, unhandled promise rejections, and HTTP 5xx API
failures are decoupled completely from the backend. The frontend container stack
and browser clients send logs directly to the monitoring stack via Vector's
HTTP receiver endpoint (`http://localhost:8686`). Vector normalizes the logs,
labels them (`service="frontend"`, `level="error"`), and ingests them directly
into Loki. The backend application performs no frontend log collection or proxying.

Docker container stdout/stderr is collected separately by Vector through the
Docker socket mount at `/var/run/docker.sock`. Container logs are written to
Loki with `source="container"` plus `container`, `image`, `stream`, and
`environment` labels.

Useful Loki examples:

```logql
{service="backend"}
{service="frontend", level="error"}
{environment="local"} |= "query"
{source="container", container=~".*server.*"}
{source="container", stream="stderr"}
```

Vector reads application logs from Kafka with:

- `bootstrap_servers`: `kafka:9092`
- `group_id`: `audql-vector-logs`
- topic: `${KAFKA_LOG_TOPIC:-audql.logs}`
- decoding: JSON
- `auto_offset_reset`: `earliest`

Vector writes application logs to Loki with JSON encoding and these labels:

- `service`
- `environment`
- `level`

Application events may contain an `event_type` field in their JSON body, but it
is not used as a Loki label because older or third-party events may omit it.
Those stable labels are what power the Grafana log filters.

Vector reads frontend logs directly via HTTP with:

- source type: `http_server`
- listen address: `0.0.0.0:8686`
- decoding: JSON
- normalized fields: `service="frontend"`, `level="error"`, `event_type="client_log"`, `environment="DEPLOY_ENV"` (defaulting to `local`)

Vector reads Docker logs with:

- source type: `docker_logs`
- Docker socket: `unix:///var/run/docker.sock`
- included containers: `text-2-sql-*`

Vector normalizes container logs before writing them to Loki:

- `source`: `container`
- `service`: container name or `unknown`
- `environment`: `DEPLOY_ENV`, defaulting to `local`
- `level`: `info`
- `event_type`: `container_log`

Container log labels in Loki:

- `source`
- `container`
- `image`
- `stream`
- `environment`

## Metrics

Prometheus scrapes:

- Django app metrics from `text2sql-server:8000/metrics/`
- HTTP blackbox probes for backend liveness, backend readiness, and frontend
- Kafka metrics from `kafka-exporter:9308`
- MySQL metrics from `mysql-exporter:9104`
- Redis metrics from `redis-exporter:9121`
- Elasticsearch metrics from `elasticsearch-exporter:9114`
- container metrics from `cadvisor:8080`
- Prometheus self-metrics

The Prometheus server keeps local metrics for `7d` through:

```yaml
--storage.tsdb.retention.time=7d
```

Current scrape jobs:

| Job | Target | Notes |
| --- | --- | --- |
| `audql-server` | `text2sql-server:8000/metrics/` | Django app metrics, scraped every 5 seconds. |
| `audql-health` | `blackbox-exporter:9115` | Probes backend live, backend ready, and frontend root URLs. |
| `kafka` | `kafka-exporter:9308` | Kafka and consumer group metrics. |
| `mysql` | `mysql-exporter:9104` | MySQL metrics. |
| `redis` | `redis-exporter:9121` | Redis metrics. |
| `elasticsearch` | `elasticsearch-exporter:9114` | Elasticsearch cluster/index metrics. |
| `containers` | `cadvisor:8080` | Docker container resource metrics. |
| `prometheus` | `prometheus:9090` | Prometheus self-scrape. |

Django app metrics:

- `audql_http_requests_total`
- `audql_http_request_duration_seconds`
- `audql_http_errors_total`

## Dashboards

Provisioned dashboards live in `observability/grafana/dashboards/`.

- `AudQL overview`: service health, request rate, latency, 5xx ratio, Kafka
  lag, MySQL status, Elasticsearch status, container CPU, and memory.
- `AudQL application logs`: log volume, error trends, and searchable newest
  first logs with service/environment/severity filters.

Datasource provisioning lives in
`observability/grafana/provisioning/datasources/`.

## Configuration files

- `observability/prometheus.yml`: scrape jobs and health probes.
- `observability/blackbox.yml`: HTTP probe module config.
- `observability/vector.yaml`: Kafka-to-Loki application log routing, HTTP
  frontend log ingestion, and Docker container log routing.
- `observability/loki-config.yaml`: Loki local storage config.
- `observability/grafana/provisioning/`: Grafana datasource and dashboard
  provisioning.

## Dashboard provisioning

Grafana mounts:

- `observability/grafana/provisioning` to `/etc/grafana/provisioning`
- `observability/grafana/dashboards` to `/var/lib/grafana/dashboards`

Provisioned datasources:

- `Prometheus` with UID `prometheus`, URL `http://prometheus:9090`
- `Loki` with UID `loki`, URL `http://loki:3100`

Dashboards are loaded into the `AudQL` folder by the dashboard provider in
`observability/grafana/provisioning/dashboards/logs.yaml`.

## Environment variables

| Variable | Default | Used by | Purpose |
| --- | --- | --- | --- |
| `DEPLOY_ENV` | `local` | backend logs | Environment label on log events. |
| `KAFKA_LOGGING_ENABLED` | `true` | backend | Enables/disables Kafka log publishing. |
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` in Compose | backend/worker | Broker list. |
| `KAFKA_LOG_TOPIC` | `audql.logs` | backend/vector | Log topic name. |
| `KAFKA_JOB_TOPIC` | `audql.jobs` | backend/worker | Background job topic. |
| `KAFKA_JOB_GROUP_ID` | `audql-workers` | worker | Worker consumer group. |
| `KAFKA_REQUEST_TIMEOUT_MS` | `15000` | worker | Kafka consumer request timeout; keep it above the session timeout. |
| `KAFKA_API_VERSION_AUTO_TIMEOUT_MS` | `5000` | worker | Kafka API-version negotiation timeout. |
| `CLIENT_LOG_RATE` | `30/min` | backend | Throttle rate for client log ingestion. |
| `VITE_ERROR_REPORTING_ENABLED` | `true` | frontend | Sends browser and 5xx API errors to backend. |
| `ADMIN_EMAIL` | `admin@example.com` | Django/Grafana | Django admin email and Grafana admin username/email. |
| `ADMIN_PASSWORD` | `change-me-local` | Django/Grafana | Shared Django and Grafana admin password. |
| `ADMIN_FIRST_NAME` | `Admin` | Django | Provisioned Django admin first name. |
| `ADMIN_LAST_NAME` | empty | Django | Provisioned Django admin last name. |

## Local troubleshooting

Check the generated Compose configuration:

```bash
docker compose config
```

Check Prometheus targets:

```bash
open http://localhost:9091/targets
```

Check Grafana dashboards:

```bash
open http://localhost:3000
```

Check that the backend exposes metrics:

```bash
curl http://localhost:8001/metrics/
```

Check Loki labels through Grafana Explore, or query Loki directly:

```bash
curl "http://localhost:3100/loki/api/v1/labels"
```

## Safety notes

The local observability stack is not hardened for public exposure. Do not expose
Grafana, Loki, Prometheus, Kafka, or exporter ports to the public internet
without authentication, authorization, TLS, and network controls.

Change `ADMIN_PASSWORD` before using this with non-development data. Grafana
reads the shared credentials when its database is first created; if you change
the local admin username or password later, recreate the development-only
`grafana_data` volume to apply both values together.
