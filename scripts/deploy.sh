#!/usr/bin/env bash
# Deploy a CI-built image from GHCR and verify it is ready.
# Usage: scripts/deploy.sh <release-tag | commit-sha | image@sha256:digest> [label]
set -euo pipefail
cd "$(dirname "$0")/.."

IMAGE_REPO="${IMAGE_REPO:-ghcr.io/abdu11ahbilal/devops-assignment-apex-arabia/task-api}"
TARGET="${1:?usage: scripts/deploy.sh <release-tag | commit-sha | image@sha256:digest> [label]}"
LABEL="${2:-$TARGET}"
PORT="$(sed -n 's/^API_PORT=//p' .env)"; PORT="${PORT:-8088}"

[[ "$TARGET" == *@sha256:* ]] && ref="$TARGET" || ref="$IMAGE_REPO:$TARGET"

echo "==> Pulling $ref"
docker pull --quiet "$ref" >/dev/null
# Deploy by digest: tags can move, digests cannot.
digest="$(docker image inspect --format '{{index .RepoDigests 0}}' "$ref")"

echo "==> Deploying $LABEL ($digest)"
docker compose up --detach --wait db
# Schema and app-role grants are applied by the admin role (idempotent); the API's role can't run DDL.
docker compose exec -T db sh -c 'psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -f /docker-entrypoint-initdb.d/01-schema.sql && sh /docker-entrypoint-initdb.d/02-app-role.sh'
API_IMAGE="$digest" docker compose up --detach --no-deps --no-build api

echo "==> Waiting for /ready on port $PORT"
for _ in $(seq 1 30); do
  if curl --fail --silent "http://127.0.0.1:$PORT/ready" >/dev/null; then
    mkdir -p .deploy
    echo "$LABEL $digest" >> .deploy/history   # known-good deployments, newest last
    echo "==> Healthy: $(curl --silent "http://127.0.0.1:$PORT/health")"
    echo "==> Deployed $LABEL"
    exit 0
  fi
  sleep 2
done

echo "!! $LABEL did not become ready within 60s. Recent API logs:" >&2
docker compose logs --tail 15 api >&2
echo "!! Investigate, then restore the last known-good release: scripts/rollback.sh" >&2
exit 1
