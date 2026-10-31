"""Run inside the API container to verify the actual runtime database privileges."""

import psycopg

from main import database_connection

with database_connection() as connection:
    role = connection.execute(
        "SELECT current_user, rolsuper, rolcreatedb, rolcreaterole "
        "FROM pg_roles WHERE rolname = current_user"
    ).fetchone()
assert role is not None and role[1:] == (False, False, False), role
try:
    with database_connection() as connection:
        connection.execute("DELETE FROM notes WHERE false")
except psycopg.errors.InsufficientPrivilege:
    print("PASS: runtime role", role[0], "is restricted and cannot DELETE notes.")
else:
    raise AssertionError("Runtime role unexpectedly has DELETE permission")
