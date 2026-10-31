# Runbook

Run from the repo root (Git Bash on Windows). API: `http://127.0.0.1:8088`.

## Deploy

```bash
scripts/deploy.sh v1.1.0
```

Pulls the image, applies `db/` (schema + API role, idempotent) as the admin, deploys the API by digest
and waits up to 60 s for `/ready`. Success is recorded in
`.deploy/history`. On failure it prints the last log lines and exits with an error.

## Roll back

```bash
scripts/rollback.sh           # last good version that isn't running now
scripts/rollback.sh v1.0.0    # or a specific version
```

Only the API container changes; the database is kept.

## When something breaks

1. **Check:** `curl /health` (is the process up?) and `curl /ready` (can it reach the DB?).
2. **Look:** `docker compose ps` and `docker compose logs --tail 50 api` — find `"level": "ERROR"`.
   In Logfire, filter on errors and open the failing request.
3. **Fix fast:** if it started after a deploy, run `scripts/rollback.sh` first, debug after.
4. **Confirm:** `/ready` returns 200 and `docker compose ps` shows `healthy`.
5. **Follow up:** release a fix as a new version, and add a check that would have caught it.

## Common problems

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `/health` OK, `/ready` 503 | API can't reach the DB, or its role lacks grants | `docker compose logs api`, check `.env`, rerun `deploy.sh` (re-applies grants) |
| `permission denied for table tasks` | Expected for `DELETE`/DDL: the API role is read + insert only | Run admin changes with `POSTGRES_USER` |
| `deploy.sh` fails on pull | Version not published (CI failed) | Check the Actions run for that commit |
| Nothing in Logfire | No/invalid `LOGFIRE_TOKEN` | App still works; use `docker compose logs` |
| Port 8088 in use | Another app | Change `API_PORT` in `.env` |

## Useful commands

```bash
docker compose logs -f api                      # live logs
curl -s http://127.0.0.1:8088/metrics           # metrics
cat .deploy/history                             # deployed versions
docker compose down                             # stop, keep data (-v deletes data)
```
