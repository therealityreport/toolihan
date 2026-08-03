# Production Observability

Use when production or staging behavior, deploys, logs, traces, metrics, or
customer impact are the main evidence.

## Evidence To Capture

- Impacted users, endpoints, regions, tenants, or data cohorts.
- Start time, end time, deploys, config changes, feature flags, and migrations.
- Logs, trace IDs, metrics, alerts, error samples, and request IDs.
- Rollback, mitigation, or scaling actions already taken.
- Difference between production, staging, and local behavior.

## First Probes

- Build a timeline before changing code.
- Correlate error rate, latency, saturation, and deploy/config events.
- Separate bad deploy, dependency outage, data issue, resource pressure, and traffic shape.
- Prefer read-only queries and sanitized samples.

## Stop Conditions

- Data access is missing or unsafe.
- Mitigation requires production mutation without explicit approval.
- Available logs cannot identify the failing service, version, or request class.

## Handoff Line

`Production proof: impact=<scope>, window=<time>, deploy=<id>, strongest_signal=<log/trace/metric>.`
