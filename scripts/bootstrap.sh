#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--no-build" ) ]]; then
  echo "Usage: bash scripts/bootstrap.sh [--no-build]" >&2
  exit 2
fi

python3 scripts/configure_env.py
docker volume create apex-postgres-data >/dev/null

if [[ "${1:-}" == "--no-build" ]]; then
  # CI supplies the image it just built. Otherwise use the saved .env selection.
  build_flag=--no-build
else
  export API_IMAGE=apex-operations-api:0.3.0
  build_flag=--build
fi

docker compose config --quiet
docker compose up -d --wait --wait-timeout 120 db
# Initializers only run automatically on empty storage. Apply grants explicitly
# as well, making bootstrap work with the candidate's existing database volume.
docker compose exec -T db sh /docker-entrypoint-initdb.d/002-app-role.sh
docker compose up -d "$build_flag" --wait --wait-timeout 120 api
python3 scripts/smoke.py --expected-version 0.3.0
if [[ -n "${API_IMAGE:-}" ]]; then
  python3 scripts/configure_env.py --image "$API_IMAGE"
fi
echo "Bootstrap complete: http://127.0.0.1:8001/docs"
