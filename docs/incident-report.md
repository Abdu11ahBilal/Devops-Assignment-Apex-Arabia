# Controlled incident: PostgreSQL unavailable

## Scope and trigger

This was an intentional local fault injection using synthetic assessment data, not a production incident. The candidate stopped only the Compose `db` service while leaving the API running. The recorded start time is `2026-10-31 15:56:55 UTC` (`evidence/incident-start.txt`).

## Observations

1. `/health` continued returning 200: the API process still handled requests.
2. `/ready` returned 503 while PostgreSQL was stopped.
3. Compose service state showed the database stopped while the API remained running.
4. PostgreSQL logs recorded shutdown; API JSON logs recorded readiness requests returning 503.
5. Starting `db` restored readiness to 200 after PostgreSQL accepted connections.
6. Notes remained available; the API did not require a restart.

## Diagnosis and recovery

The directly induced cause was database service unavailability. Correlating health/readiness responses, service state and database logs distinguished that from API process failure. Recovery was `docker compose start db`, followed by readiness and saved-data verification.

No claim is made that every 503 has this same cause: wrong credentials, a missing schema or other database/configuration faults also need investigation.

## Evidence

- `evidence/incident-health.txt`
- `evidence/incident-readiness.txt`
- `evidence/incident-services.txt`
- `evidence/incident-api.log`
- `evidence/incident-database.log`
- `evidence/incident-recovery.txt`
- `evidence/incident-recovered-notes.json`

## Follow-up

Keep separate liveness/readiness checks, add external readiness alerting before production, retain sanitized structured logs, and test backup restoration separately. A Docker health status alone does not establish business availability. This report does not invent an incident duration or MTTR that was not measured.
