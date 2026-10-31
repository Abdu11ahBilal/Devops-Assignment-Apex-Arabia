# Decision memo

## Objective and choices

Deliver a small, reviewable local system with an honest path from source commit to a verified release. FastAPI keeps Python application code small. PostgreSQL provides a real dependency and durable records for failure and persistence tests. Compose avoids paid resources while recording the complete deployment configuration.

Application features deliberately stay limited to notes and operational endpoints. CI, reproducibility, observability, security and rollback receive the effort instead of unrelated product features. Kubernetes, Terraform, public ingress and live AWS resources are outside this assessment's needs.

## Release safety

CI blocks publication on failed lint/tests, Python dependency audit, real-stack integration, restricted-role verification, scanner execution, or fixable HIGH/CRITICAL image findings. Other image findings remain visible and require review. A failed check demonstrably skipped the dependent build before restoration of the green baseline; links are in `evidence/ci-gate.txt`.

Images are tagged by commit, with source/revision OCI labels. Deployment uses exact registry digests. A human deploys locally after CI publishes; this is continuous integration and gated delivery, not unattended deployment to a laptop. The deployment script verifies readiness, application version and selected image identity. Manual rollback is executable and was demonstrated with data retained.

Runtime dependency versions, Python/PostgreSQL base images and GitHub actions are pinned. Test-tool ranges remain in `requirements-dev.txt` with application constraints. These controls improve repeatability; they are not a claim of fully hermetic bit-for-bit builds across all machines and dates.

## Operational behaviour

Health and readiness are separate to distinguish a responding process from a usable dependency path. Request logs use JSON with UTC timestamps, status, duration, version and correlation IDs. Secrets, bodies, query strings and arbitrary unmatched URLs are excluded from this application request log. Startup/error output from Uvicorn is separate.

The external named volume is independent of container lifecycle. It is explicitly reused by Compose. Initial schema creation is idempotent and occurs on empty storage; role provisioning also handles existing assessment storage. The runtime database account has only the privileges required by the application.

## Trade-offs and next improvements

- Local, single API/database instance: no HA, failover or zero-downtime releases.
- No authentication/TLS: bind to localhost and use synthetic data; add authentication, authorization, HTTPS and rate limits before public use.
- One short-lived database connection per request: simple to explain; add a bounded pool after measuring load.
- Readiness checks database connectivity, not every schema permission or business operation; smoke tests separately check writes/reads.
- Generic 503 responses avoid leaking details but can also represent configuration/query errors; expand sanitized diagnostic events for production.
- Database rollback is not covered by application image rollback; plan compatible migrations and tested backups.
- Metrics/alerts and cloud hosting are proposals, not deployed capabilities.
- Vulnerability scans have known residual findings; see the security document. Passing the configured policy is not production security approval.
- The deployment script checks a fixed local port; changing it requires updating smoke checks and documentation together.

With more time: automated restoration tests, authentication, connection pooling, resource/load measurements, enforced signed image policy, comprehensive integration tests for outage/recovery, and deployment approval environments.
