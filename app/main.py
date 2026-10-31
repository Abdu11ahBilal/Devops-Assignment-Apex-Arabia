import logging
import os
import time
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app import database
from app.logging_config import configure_observability
from app.models import Task, TaskCreate

VERSION = os.getenv("APP_VERSION", "dev")
configure_observability(VERSION)
log = logging.getLogger("apex.api")

REQUESTS = Counter("http_requests_total", "HTTP requests served", ["method", "path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["path"])
TASKS_CREATED = Counter("tasks_created_total", "Tasks created")
QUIET_PATHS = {"/health", "/ready", "/metrics"}  # probed every few seconds


@asynccontextmanager
async def lifespan(_: FastAPI):
    # No DB work at startup: if PostgreSQL is unreachable the API stays alive, /health
    # answers and /ready reports the problem instead of crash-looping.
    log.info("api started", extra={"version": VERSION})
    yield


app = FastAPI(title="Apex Task API", version=VERSION, lifespan=lifespan)
logfire.instrument_fastapi(app, excluded_urls="/health,/metrics")


@app.middleware("http")
async def observe(request: Request, call_next):
    start, status = time.perf_counter(), 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = route.path if route else "unmatched"  # route template keeps label cardinality low
        elapsed = time.perf_counter() - start
        REQUESTS.labels(request.method, path, status).inc()
        LATENCY.labels(path).observe(elapsed)
        if path not in QUIET_PATHS:
            log.info(
                "request",
                extra={"method": request.method, "path": path, "status": status,
                       "duration_ms": round(elapsed * 1000, 1)},
            )


@app.get("/health")
def health():
    """Liveness: the process is up. Deliberately does not touch the database."""
    return {"status": "ok", "version": VERSION}


@app.get("/ready")
def ready():
    """Readiness: PostgreSQL is reachable and the tasks table is readable."""
    try:
        database.ping()
    except Exception as exc:
        log.error("readiness check failed", extra={"error": str(exc).strip()})
        return JSONResponse({"status": "not ready"}, status_code=503)
    return {"status": "ready"}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    created = database.create_task(task.title)
    TASKS_CREATED.inc()
    return created


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    return database.list_tasks()


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
