# Decision memo

**Assumptions:** one small API, one database, one machine, fake data, no paid cloud.

## Choices

| Choice | Why | Trade-off |
| --- | --- | --- |
| FastAPI + plain SQL | Small and easy to explain | No migration tool yet (Alembic next) |
| Separate `/health` and `/ready` | A DB outage marks the app "not ready" instead of restarting it | — |
| Docker Compose | One command, easy to reproduce | A few seconds of downtime per deploy |
| Build once, tag later | The released image is exactly the tested one | Can only release commits that passed CI |
| Deploy by digest | Tags can move, digests can't | History is a local file |
| Manual deploy | A person approves each release | Automatic deploy to a VM is the next step |

## Security

- **Secrets:** only in `.env`, which git ignores. CI uses GitHub's short-lived token. Logfire is optional.
- **Least privilege:** CI is read-only by default; only the publishing jobs can write images.
  The container runs as a normal user with a read-only filesystem and no extra Linux permissions.
  Ports listen on localhost only.
- **Supply chain:** GitHub Actions pinned to exact commits. Trivy is pinned to a safe version,
  because Trivy itself was hacked in March 2026 (CVE-2026-33634). Trivy blocks images with
  fixable HIGH/CRITICAL vulnerabilities.
- **Known gaps:** no API login, no TLS to the local DB, `.env` is plain text.

## Alerts

| Alert | Condition |
| --- | --- |
| Not ready | `/ready` failing for 2 minutes |
| Errors | more than 5% of requests return 5xx |
| Slow | 95th-percentile latency above 500 ms for 10 minutes |

## Moving to the cloud cheaply

1. **One small VM** (Hetzner ≈ €4/month, Lightsail ≈ $10): install Docker, copy the repo files and
   `.env`, run `scripts/deploy.sh`. Add Caddy for HTTPS and a nightly `pg_dump` backup.
2. **Auto-deploy:** a GitHub Actions job, approved by a reviewer, SSHes to the VM and runs
   `deploy.sh "$TAG" || rollback.sh`.
3. **When it grows:** managed Postgres first, then a managed container service. Kubernetes only
   when there are many services.

## Next improvements

Alembic migrations · locked dependencies + Dependabot · automatic rollback · Prometheus + Grafana ·
Release Please for version numbers · zero-downtime (blue/green) deploys.
