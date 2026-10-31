#!/bin/sh
# Creates the restricted role the API connects with: read and insert tasks, nothing else
# (no DELETE, no DDL, not a superuser). Idempotent; safe to run on every deploy.
# Values are read with \getenv and quoted with %I/%L, so they can't inject SQL.
set -e
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 --quiet <<'SQL'
\getenv app_user APP_DB_USER
\getenv app_password APP_DB_PASSWORD
\getenv database POSTGRES_DB
SELECT format('CREATE ROLE %I LOGIN', :'app_user')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_user') \gexec
SELECT format('ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L',
              :'app_user', :'app_password') \gexec
GRANT CONNECT ON DATABASE :"database" TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";
GRANT SELECT, INSERT ON TABLE tasks TO :"app_user";
GRANT USAGE ON SEQUENCE tasks_id_seq TO :"app_user";
SQL
