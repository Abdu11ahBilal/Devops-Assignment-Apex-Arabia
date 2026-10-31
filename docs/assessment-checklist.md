# Assessment requirements and review map

This map distinguishes implemented behaviour, saved demonstrations and proposals. The final GitHub run/artifacts and candidate's local final verification should be inspected alongside the source.

| Requirement | Implementation / evidence |
| --- | --- |
| Minimal Dockerized API | `main.py`, `Dockerfile`; health/readiness/version/notes endpoints |
| Non-root execution | Dockerfile UID 10001; `evidence/nonroot-user.txt`; CI runtime-user assertion |
| CI installs dependencies, lints, tests and builds | `.github/workflows/ci.yml` |
| Failed checks block release path | `needs: checks`; intentional failure/skipped build and restored success in `evidence/ci-gate.txt`; publication follows checks and verification |
| Compose API and database | `compose.yaml`; internal service DNS; `evidence/compose-services.txt` |
| Configuration and persistent storage | Generated ignored `.env`; external volume; bootstrap and schema; `evidence/database-volume.txt` |
| Persistence demonstrated | Before/after container replacement JSON and `evidence/persistence-result.txt` |
| Versioned release and rollback | GHCR commit tags/digests; `scripts/deploy.sh`; release/rollback logs and version JSON |
| Structured logs and health checks | JSON middleware; `tests/test_logging.py`; Docker/PostgreSQL health checks |
| Metrics/alert proposal | `docs/observability.md`; explicitly not deployed |
| One failure investigation | `docs/incident-report.md`; `evidence/incident-*` |
| Secrets and least privilege | `docs/security.md`; role initializer/check; private env generation; OS/container controls |
| Dependency/image scanning | Saved audit JSON; CI reports and gate policy; residual findings disclosed |
| Cost-aware cloud path | `docs/cloud-plan.md`; proposal only, no paid resources used |
| At least six automated checks | 18 pytest cases plus real-stack smoke, database-role check, lint, audits and image verification |
| Intentional failed check | Local failed/passing pytest evidence plus failed/skipped-build and restored-green GitHub runs |
| Runbook and exact setup | README fresh checkout instructions and `docs/runbook.md` |
| Architecture/process diagram | Mermaid diagram in README, rendered by GitHub |
| Concise decision memo | `docs/decision-memo.md` |
| Specific AI-use disclosure | `docs/ai-use-disclosure.md` |

## Final verification before emailing

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -c requirements.lock
python -m ruff check main.py tests scripts
python -m pytest -v
bash scripts/bootstrap.sh
docker compose exec -T api python - < scripts/check_db_role.py
python3 scripts/smoke.py --expected-version 0.3.0
git status --short
git check-ignore .env
```

Save final outputs and ensure the latest CI run is green, the published image is accessible, and all required files are committed. CI's fresh runner independently exercises clean configuration/storage creation; a repeated local bootstrap alone is not evidence of a clean checkout.

Do not include secrets, `.venv`, copied production data or original company onboarding contracts. Review the generated email draft; the candidate sends it personally and schedules the assessment review after submission.
