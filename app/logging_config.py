"""Structured JSON logs on stdout, mirrored to Pydantic Logfire when LOGFIRE_TOKEN is set."""

import json
import logging
import os
import sys

import logfire

# Attributes every LogRecord has; anything else was passed via `extra=` and becomes a JSON field.
_STANDARD_ATTRS = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "color_message"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        entry.update({k: v for k, v in record.__dict__.items() if k not in _STANDARD_ATTRS})
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def configure_observability(version: str) -> None:
    # No token (local tests, CI) -> nothing is exported; the app never depends on Logfire being up.
    logfire.configure(
        service_name="apex-task-api",
        service_version=version,
        environment=os.getenv("APP_ENV", "local"),
        send_to_logfire="if-token-present",
        console=False,
    )
    logfire.instrument_psycopg()

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(JsonFormatter())
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        handlers=[stdout, logfire.LogfireLoggingHandler()],
        force=True,
    )
    # Route uvicorn's server logs through the same JSON handlers (access logs stay off:
    # the request middleware already writes one structured line per request).
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
