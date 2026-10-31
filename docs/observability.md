# Observability and alert proposal

## Implemented

- `/health`: process liveness; used by the Docker image health check.
- `/ready`: executes a bounded database query; returns 503 on database/configuration failure.
- Structured application request logs: UTC timestamp, event, generated request ID, method, matched route template, HTTP status, duration in milliseconds, and application version.
- `X-Request-ID` response header links a request with its log event.
- Logs go to stdout for `docker compose logs`; credentials, payloads and query strings are not recorded by this request logger.
- Real controlled database-outage/recovery evidence is in `evidence/incident-*`.

API liveness may remain healthy while readiness fails. An unhealthy Docker status is an observation, not a promise that Docker will automatically restart a container. The current Compose deployment does not install an alert manager or external log collector.

## Proposed metrics — not deployed

| Signal | Suggested measurement | Initial alert proposal |
| --- | --- | --- |
| Readiness | Probe `/ready` every 15 seconds | Three consecutive failures; route to operator |
| Request errors | HTTP 5xx count/rate by matched route and version | Over 5% for 5 minutes with at least 20 requests; use absolute failure alerts for low-traffic periods |
| Latency | Request-duration histogram | p95 over 500 ms for 5 minutes; tune after measuring normal behaviour |
| Database | Connection failures, query latency, connections in use | Connection failures for 1 minute or sustained saturation |
| Host/container | Memory, CPU, restart count and disk/volume usage | Disk above 80% for 10 minutes; rising restarts or sustained memory pressure |

Thresholds are starting assumptions, not measured SLOs. Exclude routine health probes from business traffic/error calculations. Never use request IDs, note contents or user IDs as metric labels, to avoid sensitive data and unbounded cardinality.

## Collection path

For a larger deployment, add Prometheus instrumentation or a log-to-metrics collector, a dashboard and alert routing. Collect JSON stdout logs centrally with retention/access limits, filter by request ID, and record the image digest alongside deployments. Alerts should link the runbook and active release. Scrubbing secrets and minimizing retained personal data remain required.
