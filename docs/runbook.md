# Operational runbook — Apex Task API

All commands run from the repository root in Git Bash (Windows) or any POSIX shell (Linux/macOS).
The Compose project is `apex-tasks`; the API listens on `http://127.0.0.1:8088` (`API_PORT` in `.env`).

## 1. Deploy a release

Pre-checks:
1. The commit's CI run is green (lint, tests, non-root check, Trivy) — otherwise no image exists.
2. The release tag exists in GHCR: `docker manifest inspect ghcr.io/abdu11ahbilal/devops-assignment-apex-arabia/task-api:v1.0.0`.

```bash
scripts/deploy.sh v1.0.0
```

What it does: pulls the tag, resolves it to an immutable `@sha256` digest, starts/keeps PostgreSQL,
replaces only the `api` container, and waits up to 60 s for `/ready`. On success it appends
`<label> <digest>` to `.deploy/history` (the list of known-good releases). On failure it prints the
last API log lines and exits non-zero — nothing is recorded as known-good.

Post-checks:
```bash
curl -s http://127.0.0.1:8088/health        # version = commit SHA of the image
curl -s http://127.0.0.1:8088/ready
docker compose ps                            # api should be "healthy"
```

## 2. Roll back

```bash
scripts/rollback.sh            # newest known-good digest that is not the one running now
scripts/rollback.sh v1.0.0     # or an explicit release tag / digest
```

Only the `api` container is replaced; the `pgdata` volume is never touched. The script prints the
`tasks` row count before and after and fails if it changed. Database schema changes must stay
backward compatible (expand → migrate → contract) for this to remain safe.

## 3. Incident response

| Step | Action |
| --- | --- |
| Detect | `deploy.sh` fails readiness, `docker compose ps` shows `unhealthy`, `/ready` returns 503, or an alert fires (see decision memo for proposed alerts). |
| Triage (≤5 min) | `curl /health` (process alive?) vs `curl /ready` (dependencies?). `docker compose ps`. |
| Investigate | `docker compose logs --tail 50 api` — JSON lines, look for `"level": "ERROR"`. In Logfire filter `service_name = 'apex-task-api'` and `level >= error`; open the `GET /ready` trace to see the failing `connect` span and its exception. |
| Mitigate | If the problem started with a deploy: `scripts/rollback.sh` first, debug second. |
| Verify | `/ready` 200, `docker compose ps` healthy, row count unchanged, error rate back to zero in Logfire / `/metrics`. |
| Follow up | Fix forward with a new tag (never re-use a tag), add a test/CI check that would have caught it, write a short post-incident note in `evidence/`. |

## 4. Troubleshooting

| Symptom | Likely cause | Check / fix |
| --- | --- | --- |
| `/health` 200, `/ready` 503 | API cannot reach PostgreSQL (DB down, wrong credentials, TLS mismatch) | `docker compose logs api \| grep readiness`; `docker compose ps db`; compare `.env` with `.env.example` |
| `deploy.sh` fails at `docker pull` | Tag not published (CI failed or tag not pushed yet), or no network | Check the Actions run for that commit; `docker manifest inspect <ref>` |
| Container restarting | Startup crash | `docker compose logs api`; `docker inspect --format '{{.State.ExitCode}}' apex-tasks-api-1` |
| No data in Logfire | `LOGFIRE_TOKEN` empty/invalid or no outbound HTTPS | The app keeps working without Logfire; rely on `docker compose logs` |
| `POST /tasks` returns 422 | Invalid input (blank or >200-char title) | Expected behaviour |
| Port 8088 busy | Another local service | Change `API_PORT` in `.env`, redeploy |

## 5. Routine operations

```bash
docker compose logs -f api                                   # live JSON logs
curl -s http://127.0.0.1:8088/metrics | grep http_requests   # request counters
cat .deploy/history                                          # deployment history (known-good)
docker compose exec db pg_dump -U apex apex > backup.sql     # ad-hoc backup before risky changes
docker compose down                                          # stop (data kept); add -v ONLY to wipe data
```
