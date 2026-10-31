# Operations runbook

Run commands from the repository root in Bash/WSL2. Keep `.env` local. Do not paste full `docker inspect` or resolved Compose configuration into public evidence: container environment values can contain passwords.

## Initial setup and ordinary operation

```bash
bash scripts/bootstrap.sh
docker compose ps
curl -i http://127.0.0.1:8001/ready
docker compose logs --no-color --tail 30 api
```

Bootstrap upgrades an existing demo database to a separate restricted runtime role without deleting notes. On a new volume, initialization creates the schema and role. Never replace an existing `.env` with newly generated administrator credentials unless the database password is deliberately rotated too: PostgreSQL initialization variables do not reset an existing database password.

Stop services: `docker compose stop`. Resume the configured deployment: `docker compose up -d --no-build --wait`. Remove Compose containers/network: `docker compose down`. The external `apex-postgres-data` volume is managed separately and retained. Do not delete it during normal deploys or rollback.

## Deploy a checked release

1. Confirm the source commit's CI run is successful and publication completed.
2. Record the current digest and expected application version in release notes.
3. Use the GHCR digest from the new run summary, not a floating `latest` tag.

```bash
docker inspect "$(docker compose ps -q api)" --format '{{.Config.Image}}'
curl -fsS http://127.0.0.1:8001/version
bash scripts/deploy.sh 'ghcr.io/OWNER/IMAGE@sha256:FULL_DIGEST' EXPECTED_VERSION
curl -fsS http://127.0.0.1:8001/notes
```

Replace placeholders with actual recorded values. A successful script exits zero after checking container image identity, `/ready`, and `/version`. It saves `API_IMAGE` in `.env`. Do not run `docker compose build` against a digest-selected image; use bootstrap for an intentional local source build.

## Manual rollback

```bash
bash scripts/deploy.sh 'ghcr.io/OWNER/IMAGE@sha256:PREVIOUS_DIGEST' PREVIOUS_VERSION
curl -i http://127.0.0.1:8001/ready
curl -fsS http://127.0.0.1:8001/notes
```

Only the API is replaced. PostgreSQL and the named volume remain. If a deployment command fails, the new container may still be running or unhealthy: inspect service state and explicitly run the previous known-good deployment command. The script does not implement automatic rollback. A digest identifies exact bytes; `/version` is a human-maintained label.

The demonstrated rollback keeps the same schema. Destructive or incompatible migrations need a separate migration/backup/restore plan; rolling back an image does not undo a migration. Expect a brief interruption during API replacement; this is not zero-downtime deployment.

## Database-outage investigation

```bash
docker compose stop db
curl -i http://127.0.0.1:8001/health
curl -i http://127.0.0.1:8001/ready
docker compose ps -a
docker compose logs --no-color --tail 60 api
docker compose logs --no-color --tail 30 db
docker compose start db
```

Expected during outage: health 200, readiness 503, database stopped, and JSON request logs with `/ready` status 503. After PostgreSQL accepts connections, readiness returns to 200 without restarting the API. Verify notes remain. Compose's startup dependency does not continuously stop/restart the API if PostgreSQL later fails. Docker's API health check intentionally checks liveness, so it can remain healthy during a database outage.

## Troubleshooting

| Symptom | Checks and action |
| --- | --- |
| Port 8001 occupied | Identify the listener with `ss -ltnp`; stop only the known conflicting process or consistently change Compose, smoke/deploy URLs and documentation |
| Container `Created`, empty logs | Start it and read the Docker error; application execution may not have begun |
| GHCR unauthorized | Confirm package visibility or use an appropriately scoped local login; do not put tokens in the repository |
| API ready 503, database healthy | Check role provisioning, matching local configuration, service hostname `db`, port 5432, and whether the schema exists; rerun bootstrap if migrating the existing demo |
| API health 200, ready 503 | Investigate database availability/configuration, rather than repeatedly restarting the API |
| Missing external volume | `docker volume inspect apex-postgres-data`; bootstrap creates it for a fresh deployment |
| TestClient deprecation warning | Current tests pass; track migration of the test HTTP client separately from runtime behaviour |

## Verify least privilege

```bash
docker compose exec -T api id
docker compose exec -T api python - < scripts/check_db_role.py
```

Expected: OS UID 10001; runtime database role lacks superuser/create-role/create-database privileges and cannot DELETE notes. The service needs SELECT and INSERT, not DELETE or schema ownership.

## Backup proposal

Not a demonstrated restore: these are proposed operational procedures. Persistence evidence alone does not prove disaster recovery.

```bash
mkdir -p .backups
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > ".backups/operations-$(date -u +%Y%m%dT%H%M%SZ).sql"
```

Protect backups as sensitive data, encrypt off-host copies, define retention and test restoration into an isolated database before relying on them. `.backups/` is excluded from Git and Docker build context. Never test a restore by overwriting the only working database.
