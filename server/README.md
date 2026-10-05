# AudQL backend

The backend is a Django and Django REST Framework application. The maintained
developer guide is [Backend](../docs/BACKEND.md); the repository-level
[README](../README.md) covers the full architecture, local stack, and
deployment.

## Local development

### Using Docker Compose

Ensure the shared external network exists (`docker network create text-2-sql-app-net`),
then start the backend and data stack:

```bash
# From repository root
docker compose -f server/compose.yaml up --build -d

# Or from server/ directory
docker compose up --build -d
```

To build the image without starting:

```bash
docker compose -f server/compose.yaml build
```

### Standalone development and tests

For backend tests, no Compose services are needed:

```bash
cd server
python -m pip install -r requirements-test.txt
pytest
```

### Populating demo data

To generate large-volume demo data (products, customers, orders, queries):

```bash
docker compose -f server/compose.yaml exec text2sql-server python manage.py populate_fake_data
```

Tests use dedicated SQLite test settings. For API routes, configuration,
background-job behavior, search, cache, email, and FCM details, see
[Backend](../docs/BACKEND.md).
