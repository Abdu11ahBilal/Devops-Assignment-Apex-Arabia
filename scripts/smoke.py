"""Exercise a real running API and database using only the Python standard library."""

import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


def request(base, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(base + path, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as response:
        return response.status, json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8001")
    parser.add_argument("--expected-version", default="0.3.0")
    args = parser.parse_args()
    status, health = request(args.base_url, "/health")
    assert status == 200 and health == {"status": "ok"}
    status, ready = request(args.base_url, "/ready")
    assert status == 200 and ready["status"] == "ready"
    _, version = request(args.base_url, "/version")
    assert version["version"] == args.expected_version
    text = f"Synthetic smoke test {uuid4()}"
    status, created = request(args.base_url, "/notes", {"text": text})
    assert status == 201 and created["text"] == text
    _, notes = request(args.base_url, "/notes")
    assert created in notes
    try:
        request(args.base_url, "/notes", {"text": ""})
    except HTTPError as error:
        assert error.code == 422
    else:
        raise AssertionError("Empty note was accepted")
    print("PASS: health, readiness, version, real database write/read and invalid input.")
    print("Smoke test leaves one synthetic note in the database; it deletes no data.")


if __name__ == "__main__":
    main()
