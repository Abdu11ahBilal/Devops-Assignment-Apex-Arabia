# Architecture

## Pipeline

```mermaid
flowchart LR
    dev[git push] --> lint[ruff] --> test[pytest + Postgres] --> build[docker build]
    build --> nonroot[non-root check] --> smoke[smoke test /ready] --> trivy[Trivy scan]
    trivy --> push[(GHCR :commit-sha)]
    tag[git tag v1.x.y] --> promote[same image gets :v1.x.y]
    promote --> push
    push --> deploy[deploy.sh] -->|ready| history[(.deploy/history)]
    deploy -->|not ready| rollback[rollback.sh]
    history --> rollback
```

## Runtime

```mermaid
flowchart LR
    client[curl] -->|127.0.0.1:8088| api
    subgraph compose[Docker Compose: apex-tasks]
        api[api: FastAPI, non-root, read-only]
        db[(db: postgres:17)]
        vol[(volume pgdata)]
        api --> db --- vol
    end
    api --> logs[JSON logs]
    api --> logfire[Logfire traces]
```

## Code map

| File | What it does |
| --- | --- |
| `app/main.py` | Endpoints, request logging and metrics |
| `app/database.py` | Table creation and SQL queries |
| `app/models.py` | Input/output validation |
| `app/logging_config.py` | JSON logs and Logfire setup |
| `scripts/deploy.sh`, `scripts/rollback.sh` | Deploy a version, go back to the last good one |
| `.github/workflows/ci.yml` | The CI pipeline above |
