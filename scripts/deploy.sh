#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ $# -ne 2 ]]; then
  echo "Usage: bash scripts/deploy.sh IMAGE_DIGEST EXPECTED_VERSION" >&2
  exit 2
fi

image="$1"
expected_version="$2"

if [[ ! "$image" =~ ^ghcr\.io/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$ ]]; then
  echo "Provide a ghcr.io image reference pinned by its full SHA-256 digest." >&2
  exit 2
fi

test -f .env || { echo "Missing local .env configuration." >&2; exit 2; }

echo "Pulling requested image: $image"
docker pull "$image"

echo "Replacing only the API; database and volume are retained."
API_IMAGE="$image" docker compose up -d --no-build --no-deps --wait --wait-timeout 60 api

actual_image=$(docker inspect "$(docker compose ps -q api)" --format '{{.Config.Image}}')
if [[ "$actual_image" != "$image" ]]; then
  echo "Running image does not match requested digest." >&2
  exit 1
fi

python3 - "$expected_version" <<'PY'
import json
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

expected = sys.argv[1]
for attempt in range(10):
    try:
        with urlopen("http://127.0.0.1:8001/ready", timeout=4) as response:
            ready = json.load(response)
        with urlopen("http://127.0.0.1:8001/version", timeout=4) as response:
            version = json.load(response)
        if ready.get("status") == "ready" and version.get("version") == expected:
            print(f"Verified database readiness and API version {expected}.")
            break
    except (URLError, TimeoutError, OSError, ValueError):
        pass
    if attempt < 9:
        time.sleep(2)
else:
    sys.exit("Verification failed. Restore the previous image with this script; selection was not saved.")
PY

python3 - "$image" <<'PY'
import sys
from pathlib import Path

path = Path(".env")
lines = [line for line in path.read_text().splitlines() if not line.startswith("API_IMAGE=")]
lines.append(f"API_IMAGE={sys.argv[1]}")
path.write_text("\n".join(lines) + "\n")
PY

echo "Deployment verified and image selection saved: $image"
