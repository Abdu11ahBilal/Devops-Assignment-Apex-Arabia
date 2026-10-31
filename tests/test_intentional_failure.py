from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_intentionally_wrong_health_expectation():
    # Deliberately incorrect: the healthy API should return 200.
    assert client.get("/health").status_code == 503
