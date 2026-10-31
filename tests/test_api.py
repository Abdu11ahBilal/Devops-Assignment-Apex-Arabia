import uuid


def test_health_reports_liveness_and_version(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"  # INTENTIONAL FAILURE: API returns "ok"
    assert "version" in response.json()


def test_ready_when_database_is_reachable(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_503_when_database_is_unreachable(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://nobody:wrong@127.0.0.1:1/missing")
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "not ready"}  # no connection details leaked to callers


def test_created_task_is_persisted_and_listed(client):
    title = f"rotate credentials {uuid.uuid4()}"
    created = client.post("/tasks", json={"title": title})
    assert created.status_code == 201
    assert created.json()["title"] == title
    assert created.json()["done"] is False

    listed = client.get("/tasks").json()
    assert {"id": created.json()["id"], "title": title} in [
        {"id": t["id"], "title": t["title"]} for t in listed
    ]


def test_blank_or_missing_title_is_rejected(client):
    assert client.post("/tasks", json={"title": "   "}).status_code == 422
    assert client.post("/tasks", json={}).status_code == 422


def test_metrics_expose_request_and_task_counters(client):
    client.post("/tasks", json={"title": "metrics probe"})
    body = client.get("/metrics").text
    assert 'http_requests_total{method="POST",path="/tasks",status="201"}' in body
    assert "tasks_created_total" in body
