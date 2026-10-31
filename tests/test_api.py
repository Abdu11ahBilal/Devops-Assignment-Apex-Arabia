from unittest.mock import Mock

import psycopg
import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def unavailable_database(monkeypatch):
    # No real database or credentials are used in these API tests.
    monkeypatch.setenv("POSTGRES_DB", "test")
    monkeypatch.setenv("POSTGRES_USER", "test")
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    connect = Mock(side_effect=psycopg.OperationalError("Simulated outage"))
    monkeypatch.setattr(main.psycopg, "connect", connect)
    return connect


def test_health_does_not_need_database(unavailable_database):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    unavailable_database.assert_not_called()


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": main.app.version}


def test_unknown_route():
    assert client.get("/banana").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [{}, {"text": ""}, {"text": "   "}, {"text": "x" * 501}, {"text": None}],
)
def test_invalid_note_is_rejected(payload, unavailable_database):
    assert client.post("/notes", json=payload).status_code == 422
    unavailable_database.assert_not_called()


def test_readiness_reports_database_outage(unavailable_database):
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "database": "unavailable"}
    unavailable_database.assert_called_once()


def test_create_note_reports_database_outage(unavailable_database):
    response = client.post("/notes", json={"text": "A valid note"})
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    unavailable_database.assert_called_once()


def test_list_notes_reports_database_outage(unavailable_database):
    response = client.get("/notes")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    unavailable_database.assert_called_once()
