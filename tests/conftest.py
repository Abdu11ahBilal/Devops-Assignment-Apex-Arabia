import os

import pytest
from fastapi.testclient import TestClient

# Tests run against a real PostgreSQL (a service container in CI, `docker compose up db` locally).
os.environ.setdefault("DATABASE_URL", "postgresql://apex:apex@localhost:5432/apex_test")

from app.main import app  # noqa: E402  (must import after DATABASE_URL is set)


@pytest.fixture
def client():
    with TestClient(app) as test_client:  # `with` runs the startup hook, which creates the schema
        yield test_client
