# AudQL frontend

The frontend is a React, TypeScript, and Vite application. The maintained
developer guide is [Frontend](../docs/FRONTEND.md); the repository-level
[README](../README.md) covers the full application architecture, local setup,
and deployment.

## Local development

From the repository root, create `client/.env` from `client/.env.example` and
set the API origin if it is not `http://localhost:8001`.

### Using Node / npm

```bash
cd client
npm install
npm run dev
```

### Using Docker Compose

Ensure the shared network exists (`docker network create text-2-sql-app-net`),
then build and start the frontend container:

```bash
# From repository root (start container)
docker compose -f client/compose.yaml up

# Or build and start in detached mode
docker compose -f client/compose.yaml up --build -d

# Or from client/ directory
docker compose up
# Or:
docker compose up --build -d
```

To build the image without starting:

```bash
docker compose -f client/compose.yaml build
```

## Checks

```bash
npm test
npm run build
```

Tests use Vitest, jsdom, and React Testing Library. See
[Frontend](../docs/FRONTEND.md) for API/auth behavior, configuration, push
notifications, and shared UI conventions.
