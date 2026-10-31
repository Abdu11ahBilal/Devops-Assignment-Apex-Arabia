# AI-use disclosure

AI assistance was used in this submission, as permitted by the assessment conditions.

**Tool:** Claude Code (Anthropic, model Claude Opus 5.5), run locally with access to this repository,
Docker Desktop and the GitHub repository.

**What it did (from my written implementation plan):**
- Generated the application code (`app/`), tests, `Dockerfile`, `compose.yaml`, the CI workflow and
  the `deploy.sh` / `rollback.sh` scripts.
- Ran the local validation loop: lint and tests in containers, Compose deployment, Logfire export check.
- Pushed the branch and tags, monitored the GitHub Actions runs, and executed the two failure
  demonstrations (intentional CI test failure; faulty v1.0.1 deployment → investigation → rollback),
  saving the real command output under `evidence/`.
- Drafted the documentation in `docs/` and the README.
- Looked up the March 2026 Trivy supply-chain compromise (CVE-2026-33634) to choose a safe, digest-pinned Trivy version.

**What I did / own:**
- Wrote the implementation plan (stack, endpoints, pipeline stages, failure scenarios, repo layout)
  that the work followed, and chose the scope trade-offs.
- Provided access (GitHub, Docker, Logfire project) and reviewed the code, evidence and documents.
- I can explain and re-run every part live: see the README "Demo script" section.

**Verification:** nothing in `evidence/` is hand-written — every file is captured command output or
a GitHub Actions / Logfire record, and can be reproduced with the commands in the README.
