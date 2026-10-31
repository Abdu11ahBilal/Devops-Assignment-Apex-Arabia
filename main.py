"""Small Operations API for the DevOps assessment."""

import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

load_dotenv()

app = FastAPI(title="Operations API", version="0.2.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": app.version}


@app.get("/ready")
def ready():
    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=os.getenv("DB_PORT", "15432"),
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            connect_timeout=3,
            options="-c statement_timeout=3000",
        ) as connection:
            connection.execute("SELECT 1").fetchone()
    except (psycopg.Error, KeyError):
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unavailable"},
        )

    return {"status": "ready", "database": "connected"}

class NoteInput(BaseModel):
    text: str = Field(min_length=1, max_length=500)

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Note must contain non-whitespace text")
        return value.strip()


def database_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "15432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
        options="-c statement_timeout=3000",
    )


@app.post("/notes", status_code=201)
def create_note(note: NoteInput):
    try:
        with database_connection() as connection:
            row = connection.execute(
                "INSERT INTO notes (text) VALUES (%s) RETURNING id, text",
                (note.text,),
            ).fetchone()
        return {"id": row[0], "text": row[1]}
    except (psycopg.Error, KeyError):
        return JSONResponse(
            status_code=503,
            content={"detail": "Database unavailable"},
        )


@app.get("/notes")
def list_notes():
    try:
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT id, text FROM notes ORDER BY id"
            ).fetchall()
        return [{"id": row[0], "text": row[1]} for row in rows]
    except (psycopg.Error, KeyError):
        return JSONResponse(
            status_code=503,
            content={"detail": "Database unavailable"},
        )
