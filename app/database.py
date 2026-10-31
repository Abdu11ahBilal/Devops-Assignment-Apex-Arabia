"""PostgreSQL access. Every query is parameterised; connections are short-lived.

The schema lives in db/01-schema.sql and is applied by the admin role, so the API's own
role (db/02-app-role.sh) only needs SELECT and INSERT on tasks.
"""

import os

import psycopg
from psycopg.rows import dict_row


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3, row_factory=dict_row)


def ping() -> None:
    # Proves connectivity, schema and grants in one cheap query.
    with connect() as conn:
        conn.execute("SELECT 1 FROM tasks LIMIT 1")


def create_task(title: str) -> dict:
    with connect() as conn:
        return conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done, created_at",
            (title,),
        ).fetchone()


def list_tasks() -> list[dict]:
    with connect() as conn:
        return conn.execute("SELECT id, title, done, created_at FROM tasks ORDER BY id").fetchall()
