# Decision memo

**Scope assumption.** One small API, one PostgreSQL database, one host. Synthetic data only. No
Kubernetes and no paid cloud: everything runs with Docker Desktop / Docker Engine and free GitHub
features (Actions minutes on a public repo, GHCR).

## Architecture choices

| Decision | Why | Trade-off accepted |
| --- | --- | --- |
| FastAPI + psycopg 3, raw parameterised SQL | Tiny surface, explicit queries, no ORM to explain | No migrations framework (schema is one idempotent `CREATE TABLE IF NOT EXISTS`); Alembic would be next |
| Short-lived DB connection per request | Simplest code; errors surface directly in `/ready` and in traces | Connection setup cost per request; use `psycopg_pool` / PgBouncer under real load |
| Liveness (`/health`) separate from readiness (`/ready`) | A DB outage should mark the API *not ready*, not restart-loop it | Docker Compose doesn't route traffic by health, so readiness is enforced by `deploy.sh` and visible in `docker compose ps` |
| Docker Compose on one host | Reproducible with one command, matches the assessment | No zero-downtime: replacing the api container gives a few seconds of downtime |
| Build once, promote by tag | The `v1.0.0` image is byte-for-byte the image that passed tests and Trivy (`imagetools create`, no rebuild) | Release tags can only be cut from commits that already passed CI on the branch |
| Deploy by digest, not tag | Tags are mutable; `deploy.sh` resolves the tag to `@sha256:…` and records that in `.deploy/history` | History is a local file; on a team this belongs in the deployment system |
| Manual deploy after green CI | Keeps a human gate; the assessment runs locally where CI cannot reach | Continuous deployment to a VM is the next step (see below) |

## Security trade-offs

- **Secrets**: only in `.env` (git-ignored) and passed as environment variables. `.env.example`
  documents keys with placeholder values. CI uses the short-lived `GITHUB_TOKEN`; the only
  credential in CI is a throwaway Postgres password for an ephemeral service container.
  Logfire's token is optional — without it the app runs normally and nothing is exported.
- **Least privilege**: workflow default `contents: read`; only the image/release jobs get
  `packages: write`. Container runs as UID 10001 with a read-only root filesystem, `cap_drop: ALL`
  and `no-new-privileges`. The API and DB ports bind to `127.0.0.1` only; the DB isn't published.
- **Supply chain**: third-party actions pinned to commit SHAs; Trivy pinned by image digest
  (trivy-action / Trivy 0.69.4–0.69.6 were compromised in March 2026, CVE-2026-33634). Trivy fails
  the build on fixable HIGH/CRITICAL CVEs; ruff's `S` (bandit) rules catch insecure Python patterns.
  Direct dependencies are pinned; a full hash-locked lockfile (`uv lock` / `pip-compile --generate-hashes`)
  and Dependabot are the next improvement.
- **Accepted gaps** (documented, not hidden): no auth on the API (internal demo), no TLS between
  API and DB on the local network, `.env` is plaintext on disk.

## Observability and alert proposal

JSON logs on stdout (one line per request with method, route, status, duration), Logfire traces for
every request including the SQL spans, and Prometheus metrics at `/metrics`. Proposed alerts once a
Prometheus/Grafana or Logfire alerting is in place:

| Alert | Condition | Severity |
| --- | --- | --- |
| API not ready | `/ready` failing for 2 min (Docker health `unhealthy`) | page |
| Error rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05` | page |
| Latency | p95 of `http_request_duration_seconds` > 500 ms for 10 min | ticket |
| No traffic | `rate(http_requests_total[15m]) == 0` during business hours | ticket |

## Cost-aware path to cloud hosting

1. **One small Linux VM** (e.g. Hetzner CX22 ≈ €4/month, or AWS t4g.small / Lightsail ≈ $10–12/month):
   install Docker, copy `compose.yaml`, `.env` and `scripts/`, run `scripts/deploy.sh v1.x.y`.
   Put Caddy in front for automatic HTTPS; keep PostgreSQL on a named volume with nightly
   `pg_dump` to object storage (cents/month). Total ≈ $5–15/month.
2. **CD**: add a GitHub Actions `deploy` job, gated by a GitHub *environment* with required
   reviewers, that SSHes to the VM (key stored as an environment secret, VM firewall allowing only
   22/443) and runs `scripts/deploy.sh "$TAG" || scripts/rollback.sh`.
3. **When it outgrows one VM**: move PostgreSQL to a managed service (RDS/Cloud SQL, ~$15–30/month
   smallest tier, automated backups/PITR) before scaling the API; then a managed container service
   (ECS Fargate / Cloud Run) — Kubernetes only when there are many services to justify it.

## What I would improve with more time

Alembic migrations; hash-locked dependencies + Dependabot; a CI step that runs the built image
against Postgres (container smoke test — it would have caught the v1.0.1 incident before release);
automatic rollback on failed readiness; Prometheus + Grafana with the alerts above; blue/green on the
VM via two api services behind Caddy for zero-downtime deploys.
