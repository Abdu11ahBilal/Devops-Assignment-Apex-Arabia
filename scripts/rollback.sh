#!/usr/bin/env bash
# Restore the most recent known-good image that differs from what is running now.
# PostgreSQL is untouched: only the api container is replaced, the data volume stays.
# Usage: scripts/rollback.sh [release-tag | image@sha256:digest]   (default: from .deploy/history)
set -euo pipefail
cd "$(dirname "$0")/.."

running="$(docker inspect --format '{{.Config.Image}}' "$(docker compose ps --all --quiet api)" 2>/dev/null || true)"

if [[ $# -gt 0 ]]; then
  label="$1"; target="$1"
else
  [[ -s .deploy/history ]] || { echo "!! No known-good deployment recorded in .deploy/history" >&2; exit 1; }
  read -r label target < <(awk -v cur="$running" '$2 != cur { last = $0 } END { print last }' .deploy/history)
  [[ -n "${target:-}" ]] || { echo "!! No known-good image other than the running one" >&2; exit 1; }
fi

count_tasks() {
  docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT count(*) FROM tasks"'
}

echo "==> Rolling back"
echo "    from: ${running:-<nothing running>}"
echo "    to:   $label ($target)"
before="$(count_tasks)"

scripts/deploy.sh "$target" "$label"

after="$(count_tasks)"
echo "==> Tasks in PostgreSQL before: $before, after: $after"
[[ "$before" == "$after" ]] || { echo "!! Row count changed during rollback" >&2; exit 1; }
echo "==> Rollback complete, data preserved"
