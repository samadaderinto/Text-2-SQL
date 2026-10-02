# AudQL backend

The backend is a Django and Django REST Framework application. The maintained
developer guide is [Backend](../docs/BACKEND.md); the repository-level
[README](../README.md) covers the full architecture, local stack, and
deployment.

## Local development

For the complete local API, worker, database, cache, search, and broker stack,
follow the root README's Compose setup. For backend tests, no Compose services
are needed:

```bash
cd server
python -m pip install -r requirements-test.txt
pytest
```

Tests use dedicated SQLite test settings. For API routes, configuration,
background-job behavior, search, cache, email, and FCM details, see
[Backend](../docs/BACKEND.md).
