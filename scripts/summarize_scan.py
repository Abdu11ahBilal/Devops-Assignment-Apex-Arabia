"""Summarize a Trivy JSON report without suppressing findings."""

import argparse
import json
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("report")
parser.add_argument("--fail-on-fixable", action="store_true")
args = parser.parse_args()
report = json.loads(Path(args.report).read_text())
findings = [
    item
    for result in report.get("Results", [])
    for item in result.get("Vulnerabilities", [])
]
print("Image:", report.get("ArtifactName", "unknown"))
print("Findings by severity:", dict(Counter(item["Severity"] for item in findings)))
for item in findings:
    if item["Severity"] in {"HIGH", "CRITICAL"}:
        print(
            item["Severity"], item["PkgName"], item["VulnerabilityID"],
            "installed:", item["InstalledVersion"],
            "fixed:", item.get("FixedVersion") or "no fix listed",
        )
print("Report collection is not a declaration that the image is vulnerability-free.")
fixable = [
    item for item in findings
    if item["Severity"] in {"HIGH", "CRITICAL"} and item.get("FixedVersion")
]
print("High/critical package findings with a listed fix:", len(fixable))
if args.fail_on_fixable and fixable:
    raise SystemExit("Release blocked: fixable HIGH/CRITICAL image vulnerabilities.")
