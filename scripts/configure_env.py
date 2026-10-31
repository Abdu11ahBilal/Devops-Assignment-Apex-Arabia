"""Create local credentials without printing them; preserve existing settings."""

import argparse
import os
import secrets
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image")
    args = parser.parse_args()
    path = Path(".env")
    lines = path.read_text().splitlines() if path.exists() else []
    values = {}
    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    defaults = {
        "POSTGRES_USER": "apex",
        "POSTGRES_DB": "operations",
        "POSTGRES_PASSWORD": secrets.token_hex(24),
        "APP_DB_USER": "apex_app",
        "APP_DB_PASSWORD": secrets.token_hex(24),
    }
    for key, value in defaults.items():
        if not values.get(key):
            lines = [line for line in lines if not line.startswith(f"{key}=")]
            lines.append(f"{key}={value}")
            values[key] = value
    if values["POSTGRES_USER"] == values["APP_DB_USER"]:
        raise SystemExit("Bootstrap and application database users must differ.")
    if args.image:
        lines = [line for line in lines if not line.startswith("API_IMAGE=")]
        lines.append(f"API_IMAGE={args.image}")
    os.umask(0o077)
    path.write_text("\n".join(lines) + "\n")
    path.chmod(0o600)
    print("Local configuration ready; credential values were not printed.")


if __name__ == "__main__":
    main()
