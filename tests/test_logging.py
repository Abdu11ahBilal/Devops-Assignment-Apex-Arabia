import json
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.mark.parametrize("path,status", [("/health", 200), ("/banana", 404)])
def test_request_log_matches_response(monkeypatch, path, status):
    log = Mock()
    monkeypatch.setattr(main.request_logger, "info", log)
    response = client.get(path)
    log.assert_called_once()
    event = json.loads(log.call_args.args[0])
    assert response.status_code == status
    assert event["status"] == status
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert str(UUID(event["request_id"])) == event["request_id"]
    assert event["duration_ms"] >= 0
    assert event["version"] == main.app.version


def test_request_log_excludes_query_strings(monkeypatch):
    log = Mock()
    monkeypatch.setattr(main.request_logger, "info", log)
    client.get("/health?token=synthetic-sensitive-value")
    record = log.call_args.args[0]
    assert "synthetic-sensitive-value" not in record
    assert json.loads(record)["route"] == "/health"
