# AI-use disclosure

**Tool:** Claude Code (Anthropic, Claude Opus 5.5).

**I did:** wrote the implementation plan (stack, endpoints, pipeline, failure scenarios, layout),
chose the scope, gave access to GitHub, Docker and Logfire, and reviewed the code, evidence and docs.

**AI did, following that plan:**
- Wrote the app, tests, Dockerfile, Compose file, CI workflow and deploy/rollback scripts.
- Ran local checks, pushed the branch and tags, watched CI, and ran both failure demos.
- Saved the real command output in `evidence/` (nothing there is hand-written).
- Drafted these docs, and looked up the 2026 Trivy compromise to pick a safe version.

I can explain and re-run every part live.
