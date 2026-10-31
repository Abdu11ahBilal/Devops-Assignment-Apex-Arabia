import os
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

# Tests run against a real PostgreSQL (a service container in CI, a throwaway container locally).
os.environ.setdefault("DATABASE_URL", "postgresql://apex:apex@localhost:5432/apex_test")

from app.main import app  # noqa: E402  (must import after DATABASE_URL is set)

SCHEMA = Path(__file__).parents[1] / "db" / "01-schema.sql"


@pytest.fixture(scope="session", autouse=True)
def schema():
    # Same file the admin role applies in Compose and in deploy.sh.
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(SCHEMA.read_text())


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
