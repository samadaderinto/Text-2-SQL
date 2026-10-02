# AudQL frontend

The frontend is a React, TypeScript, and Vite application. The maintained
developer guide is [Frontend](../docs/FRONTEND.md); the repository-level
[README](../README.md) covers the full application architecture, local setup,
and deployment.

## Local development

From the repository root, create `client/.env` from `client/.env.example` and
set the API origin if it is not `http://localhost:8001`. Then run:

```bash
cd client
npm install
npm run dev
```

## Checks

```bash
npm test
npm run build
```

Tests use Vitest, jsdom, and React Testing Library. See
[Frontend](../docs/FRONTEND.md) for API/auth behavior, configuration, push
notifications, and shared UI conventions.
