#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p evidence

python -m ruff check main.py tests scripts | tee evidence/final-lint.txt
python -m pytest -v 2>&1 | tee evidence/final-tests.txt
bash scripts/bootstrap.sh 2>&1 | tee evidence/final-bootstrap.txt
docker compose exec -T api python - < scripts/check_db_role.py | tee evidence/final-database-role.txt
docker compose exec -T api id | tee evidence/final-runtime-user.txt
docker compose ps | tee evidence/final-compose-services.txt
curl -fsS http://127.0.0.1:8001/version | tee evidence/final-version.json
echo
curl -fsS http://127.0.0.1:8001/ready | tee evidence/final-readiness.json
echo
git check-ignore .env
echo "PASS: local final checks. Commit evidence and confirm the final GitHub run before submitting."
