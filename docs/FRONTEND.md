# Frontend

The frontend is a React, TypeScript, Vite app in `client/`. Update this
document when frontend structure, routes, API behavior, state flow, UX patterns,
or build/test behavior changes.

## Important modules

- `client/src/main.tsx`: React entrypoint.
- `client/src/App.tsx`: app shell, routing, and global toast container.
- `client/src/layouts/Header.tsx`: top navigation and common actions.
- `client/src/layouts/Sidebar.tsx`: primary navigation.
- `client/src/components/`: feature screens and form-heavy UI.
- `client/src/contexts/auth-context.tsx`: authentication state.
- `client/src/contexts/store-context.tsx`: store/domain state shared by
  screens.
- `client/src/utils/api.ts`: Axios instance, JWT attachment, refresh handling,
  and API error reporting.
- `client/src/utils/api-config.ts`: shared API-origin normalization used by
  requests and client error reporting.
- `client/src/utils/error-reporting.ts`: browser/client error capture.
- `client/src/utils/queue-jobs.ts`: queued job polling helpers.
- `client/src/styles/main.scss`: global stylesheet imports and shared toast
  styling.

## Runtime behavior

The app reads `VITE_API_BASE_URL` and defaults to `http://localhost:8001`.
Relative or hostname-only API values are normalized to HTTPS. The same resolved
origin is used for normal API calls and client error reporting.

Access and refresh tokens are stored encrypted in `localStorage`. The Axios
request interceptor decrypts the access token and attaches it as a bearer token.
The response interceptor reports HTTP 5xx API failures to the backend and tries
one refresh-token retry after a 401 response.

Queued backend actions return a job ID. UI code should poll `/jobs/<job_id>/`
through the queue helpers rather than duplicating polling logic in components.

## Configuration

Local frontend config lives in `client/.env`; the committed template is
`client/.env.example`. Do not add production env files. Production frontend
build values are configured in the Render static-site environment. GitHub
Actions secrets are used only for workflow operations, not as a
general-purpose runtime environment.

| Variable | Default in Compose | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8001` | Backend API origin used by the Axios client. |
| `VITE_ERROR_REPORTING_ENABLED` | `true` | Enables browser/client error reporting to `/logs/client/`. |
| `VITE_FIREBASE_API_KEY` | empty | Firebase web app configuration. |
| `VITE_FIREBASE_AUTH_DOMAIN` | empty | Firebase web app configuration. |
| `VITE_FIREBASE_PROJECT_ID` | empty | Firebase project used by the web SDK. |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | empty | Firebase Cloud Messaging sender. |
| `VITE_FIREBASE_APP_ID` | empty | Firebase web app identifier. |
| `VITE_FIREBASE_VAPID_KEY` | empty | Web Push VAPID key used to register the browser for FCM. |

Firebase web configuration values are bundled into the browser build and must
not contain private service-account credentials. The browser registers a
device token through the authenticated API; server-side FCM credentials are
configured separately in the backend environment. Browser push requires a
supported browser, notification permission, and a secure origin (localhost is
treated as secure for development).

The frontend has its own dedicated Docker Compose stack defined in
`client/compose.yaml` (stack name `text-2-sql-frontend`). The Vite dev server is
started inside the container with:

```bash
npm run dev -- --host 0.0.0.0 --port 4174
```

To build and run the frontend stack with Docker Compose:

```bash
docker compose -f client/compose.yaml up --build -d
```

or from within the `client/` directory:

```bash
docker compose up --build -d
```

To build the frontend Docker image without running:

```bash
docker compose -f client/compose.yaml build
```

The client Docker service is published at `http://localhost:4174`, bind-mounts
`./client` into `/app`, uses the `client_node_modules` named volume for installed
dependencies, and attaches to the shared `text-2-sql-app-net` network. That keeps
container dependencies separate from the host checkout.

## UI and feedback

Toast notifications are centralized through the global Toastify container in
`App.tsx`. Components should trigger toast events, but should not mount their
own extra containers. Toast styling lives in `client/src/styles/main.scss`.

Use smooth state transitions for long-running actions:

- show a loading toast while work is queued or running
- update the same toast when work completes or fails
- avoid stacking repeated identical notifications
- keep error messages human-readable while logging diagnostic detail elsewhere

## Error reporting

The frontend captures uncaught browser errors, unhandled promise rejections, and
server-side API failures. Events are sent to `/logs/client/` when
`VITE_ERROR_REPORTING_ENABLED` is true. Do not include request bodies,
authentication headers, or secrets in client log payloads.

## Local commands

Using Node / npm:

```bash
cd client
npm install
npm run dev
npm test
npm run build
```

Using Docker Compose:

```bash
# Start frontend container (from repository root)
docker compose -f client/compose.yaml up

# Build and start frontend container in detached mode
docker compose -f client/compose.yaml up --build -d

# Build frontend container image only
docker compose -f client/compose.yaml build

# Stop frontend container
docker compose -f client/compose.yaml down
```

The test suite uses Vitest, jsdom, and React Testing Library.
The Compose frontend is available at <http://localhost:4174>; when running Vite
directly, configure `VITE_API_BASE_URL` to the address reachable from the
browser, usually `http://localhost:8001`.

## Frontend documentation checklist

When frontend code changes, update this file if the change affects:

- routes or page structure
- API calls, authentication, token refresh, or queued job polling
- global contexts or shared state
- toasts, error handling, or client logging
- environment variables
- build, test, or development commands
- user workflows such as query generation, audio input, exports, or settings
