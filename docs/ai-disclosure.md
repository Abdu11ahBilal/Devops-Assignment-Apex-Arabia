# AI-use disclosure

AI assistance was used, as the assessment allows. **Tool:** Claude Code (Anthropic, Claude Opus 5.5).

## My work

- Wrote the implementation plan: stack, endpoints, CI stages, release and rollback approach,
  failure scenarios and repository layout.
- Designed the architecture and supplied the AWS-style reference the diagram follows.
- Set the scope and trade-offs, and directed the changes (brevity, versioning model, diagram).
- Provided access to GitHub, GHCR, Docker and Logfire.
- Reviewed the code, CI runs, evidence and documents, and can explain and re-run every part.

## AI-assisted work, from my plan and under my review

- Generated the application, tests, Dockerfile, Compose file, CI workflow and deploy/rollback scripts.
- Ran local checks, pushed the branch and release tags, and executed both failure demonstrations.
- Captured the real command output in `evidence/` (nothing there is hand-written).
- Drew `docs/architecture.svg` from my reference design and drafted these documents.
- Looked up the March 2026 Trivy compromise (CVE-2026-33634) to pin a safe Trivy version.
- Compared this branch with an earlier AI-assisted attempt (`main`, made with a different AI tool) and,
  at my request, ported its stronger security practices: restricted DB role, digest-pinned base
  images, full lockfile with `pip-audit`.
