# Containerized Development

This repository has three application services:

- `client`: Vite/React dev server on port `4174`
- `server`: Django dev server on port `8000`
- `database`: persistent MySQL 8.4 database on port `3306`
- `elasticsearch`: single-node Elasticsearch 9 search engine on port `9200`

## Run

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:4174
- Backend: http://localhost:8000

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
curl -i http://localhost:8000/health/
curl -i http://localhost:8000/health/live/
```

## Environment

The Compose file intentionally does not load `server/.env` automatically. That prevents `docker compose config` and similar commands from printing local secrets.

For local development, export only the values you need before running Compose:

```bash
export SECRET_KEY="change-me"
export OPENAI_API_KEY="sk-..."
export MYSQL_PASSWORD="change-this-database-password"
export MYSQL_ROOT_PASSWORD="change-this-root-password"
docker compose up --build
```

Without `OPENAI_API_KEY`, the app will still boot, but voice-to-SQL requests that call OpenAI will fail.

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
docker compose exec server python manage.py reindex_search --rebuild
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
- The frontend talks to `http://localhost:8000` by default through `VITE_API_BASE_URL`.

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
opens one tracked GitHub issue plus sends an SMS after three consecutive
failures. While the incident remains open, duplicate alert texts are
suppressed. When readiness recovers, the workflow closes the issue and sends a
recovery SMS if an incident alert was sent.

Configure these repository Actions secrets before enabling the monitor:

- `PRODUCTION_HEALTHCHECK_URL`: the production API URL ending in `/health/`
- `AFRICASTALKING_USERNAME`: your Africa's Talking production username
- `AFRICASTALKING_API_KEY`: the API key from your Africa's Talking account
- `INCIDENT_SMS_RECIPIENT`: the on-call phone number in E.164 format

The workflow sends SMS directly from GitHub Actions to Africa's Talking. Keep
the API key and recipient in Actions secrets; do not put them in workflow files
or commit them. Scheduled workflows run from the repository's default branch.
