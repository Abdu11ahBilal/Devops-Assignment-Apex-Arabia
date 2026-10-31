# Security controls and scan assessment

## Implemented controls

- Synthetic/public assessment data only; no production credentials or Apex systems.
- `.env` is ignored by Git and excluded from the image build context. Setup generates random local passwords and restricts file permissions to 0600.
- API receives only its runtime database credentials, not administrator credentials. PostgreSQL retains administrator configuration for initialization.
- Runtime database role has SELECT/INSERT on notes, sequence usage and schema/database access. It is not a superuser, cannot create roles/databases and cannot DELETE notes; an executable check verifies this.
- API runs as OS UID/GID 10001, drops Linux capabilities, disallows privilege escalation and has a read-only root filesystem with writable temporary storage.
- API host binding is loopback only; database port is not published. Compose's private network provides service-name discovery.
- Parameterized SQL and bounded input; database connection/query timeouts.
- Structured request logging omits credentials, bodies, headers and query strings.
- Workflow defaults to read-only repository permissions; package-write permission is limited to the build/publish job. The automatic workflow token is used only in the publication step.
- Actions and runtime base images are pinned. Deployments use application image digests.

Environment variables remain visible to users with Docker administrator access. This is local secret injection, not a production secret vault. Do not share full container inspection output or resolved Compose configuration.

## Python dependency audit

`pip-audit==2.10.1` scanned the locked runtime dependency file. The submitted local report found no known vulnerabilities and the command returned zero. CI reruns the audit strictly; findings or execution failures block the dependent build. This does not assess every possible application defect.

Evidence: `evidence/dependency-audit.json` and `evidence/dependency-scanner-version.txt`.

## Container scan findings

The submitted Trivy 0.76.1 report for the deployed 0.3.0 image reports the following **package/vulnerability entries**, not independent exploitable incidents:

- LOW: 62
- MEDIUM: 65
- HIGH: 44
- CRITICAL: 0
- UNKNOWN: 1

There are 78 distinct vulnerability IDs overall and 8 distinct HIGH IDs. None of the HIGH entries lists a fixed version in this report. Findings include Debian util-linux-related packages, ncurses, ACL, systemd-related libraries and Perl. Some IDs repeat across multiple binary packages. They have not been independently reproduced or declared unreachable. A blank fixed-version field is not proof the issue is harmless.

The original exploratory command deliberately returned zero for findings. Therefore, its zero exit code meant report collection succeeded, not that the image was clean. Full original report: `evidence/image-audit.json`.

## CI policy and residual-risk decision

CI collects the full report, including unfixed and lower-severity findings. It fails release publication on HIGH/CRITICAL entries with a listed fixed version. Scanner execution failures also fail the job. Reports are uploaded even when later steps fail. Unfixed HIGH/CRITICAL entries and lower-severity entries remain visible for review; they are not silently removed with an ignore file.

For this localhost-only, non-production assessment, the reported unfixed findings are disclosed as residual risk, with non-root execution, restricted capabilities, local-only exposure and no customer data reducing exposure. This is not production authorization or a claim that mitigation eliminates the vulnerabilities. Before production, review each advisory with the distribution/vendor, consider a smaller compatible base image, rebuild/re-scan when updates arrive, and require explicit owner approval for remaining findings.

The pinned base digest makes the selected base repeatable; it does not receive fixes automatically. Updating that pin requires rebuilding, testing and scanning. Current CI reports describe each new image independently; the historical report above remains evidence of the originally scanned digest.

## Image scanning without Docker administrator access

CI exports the built image as a tar archive and runs the scanner against that archive. It mounts only the archive directory and report directory, not the Docker socket or `.env` file. The scanner image is version-tag pinned; pinning the scanner itself by digest would further strengthen supply-chain controls.

```bash
python3 scripts/summarize_scan.py evidence/image-audit.json --fail-on-fixable
```

This applies the documented policy to a saved report; refreshing vulnerability intelligence requires a new scan.

## Remaining scope limits

There is no API authentication, HTTPS termination, abuse protection or public ingress. Backup restoration and production secret management are proposals. Restrict use to the local synthetic-data assessment until those controls are implemented and tested.
