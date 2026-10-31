"""PostgreSQL access. Every query is parameterised; connections are short-lived."""

import os

import psycopg
from psycopg.rows import dict_row

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    title      TEXT        NOT NULL,
    done       BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3, row_factory=dict_row)


def init_schema() -> None:
    with connect() as conn:
        conn.execute(SCHEMA)


def ping() -> None:
    with connect() as conn:
        conn.execute("SELECT 1")


def create_task(title: str) -> dict:
    with connect() as conn:
        return conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done, created_at",
            (title,),
        ).fetchone()


def list_tasks() -> list[dict]:
    with connect() as conn:
        return conn.execute("SELECT id, title, done, created_at FROM tasks ORDER BY id").fetchall()
