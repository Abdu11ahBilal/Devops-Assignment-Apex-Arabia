-- Applied by the admin role: on an empty volume by the postgres entrypoint, and on
-- every deploy by scripts/deploy.sh. Must stay idempotent and backward compatible.
CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    title      TEXT        NOT NULL,
    done       BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
