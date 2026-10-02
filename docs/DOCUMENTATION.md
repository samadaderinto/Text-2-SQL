# Documentation maintenance

These docs are part of the codebase. Update them in the same change whenever
behavior changes.

## What to update

- Update the [root README](../README.md) when system-level data flow,
  architectural choices, local setup, or deployment behavior changes.
- Update [Backend](BACKEND.md) when API endpoints, settings, models, jobs,
  permissions, metrics, logs, or health checks change.
- Update [Frontend](FRONTEND.md) when routes, shared state, API calls, token
  behavior, toasts, error reporting, or user workflows change.
- Update [Observability](OBSERVABILITY.md) for monitoring-stack Compose,
  logs, metrics, probes, exporters, ports, labels, dashboards, or alerting.
  Keep application Compose startup, ports, and local environment-file
  instructions in the [root README](../README.md) and relevant package guide.
- Update [server/README.md](../server/README.md) and
  [client/README.md](../client/README.md) when package-specific setup or test
  commands change.

## Pull request checklist

Before calling work done, check whether the change altered any documented
behavior. If yes, update the matching docs in the same patch.

Documentation does not need to repeat every implementation detail. It should
explain the stable contracts that future contributors need: where things live,
how data moves, what endpoints exist, what commands run, and what operational
signals matter.

## Config documentation rule

When adding a tool, dependency, service, exporter, dashboard, environment
variable, queue topic, port, volume, or runtime command, document:

- what it is called
- where it is configured
- which service uses it
- its default local value
- whether it is safe only for local development
- how to verify it is working

Environment files are intentionally constrained:

- backend local values: `server/.env`
- backend template: `server/.env.example`
- frontend local values: `client/.env`
- frontend template: `client/.env.example`

Do not add root `.env`, `.env.production`, `.env.local`, service-specific env
files, or special env files in other directories. Configure production runtime
values in the deployment provider; use GitHub Actions secrets only for workflow
operations and values explicitly checked by workflows.
