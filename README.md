# AudQL

AudQL is a text-to-SQL application with a React/Vite frontend, a Django REST
backend, MySQL persistence, Elasticsearch search, Kafka-backed background jobs,
and a local observability stack built around Prometheus, Loki, Vector, and
Grafana.

## Developer documentation

Keep these documents updated whenever the code changes:

- [Architecture](docs/ARCHITECTURE.md): system map, service boundaries, data
  flow, and operational behavior.
- [Backend](docs/BACKEND.md): Django app structure, API surface, background
  jobs, metrics, health checks, and tests.
- [Frontend](docs/FRONTEND.md): React app structure, API client behavior,
  routing, toasts, client error reporting, and tests.
- [Observability](docs/OBSERVABILITY.md): logs, metrics, dashboards, probes,
  exporters, and local Grafana usage.
- [Documentation maintenance](docs/DOCUMENTATION.md): what must be updated as
  the code evolves.

Existing setup notes are still available in [CONTAINERIZATION.md](CONTAINERIZATION.md),
[server/README.md](server/README.md), and [client/README.md](client/README.md).

## Local stack

```bash
docker compose -f compose.yaml up --build
```

This starts the frontend and backend together. The browser-facing contract is
`http://localhost:4174` -> `http://localhost:8001`; the frontend gets that API
origin from `client/.env` / `VITE_API_BASE_URL`.

Start monitoring separately when you want Grafana, Prometheus, Loki, Vector,
and exporters:

```bash
docker compose -f monitoring/compose.yaml up
```

Local URLs:

- Frontend: <http://localhost:4174>
- Backend: <http://localhost:8001>
- API docs: <http://localhost:8001/docs/swagger/>
- Grafana: <http://localhost:3000>
- Prometheus: <http://localhost:9091>

Default local Grafana credentials are `admin` / `change-me-local`.

## Fast checks

Backend:

```bash
cd server
python -m pip install -r requirements-test.txt
pytest
```

Frontend:

```bash
cd client
npm test
npm run build
```
