# Switchboard

Feature flag service. Backend is Flask and SQLAlchemy, admin UI is React.

## How a flag evaluates

1. If the flag is disabled, everyone gets `default_variant`.
2. Targeting rules are checked in priority order. First match wins and returns that rule's variant. A rule either carries its own attribute and operator, or points at a segment.
3. If no rule matches, the user is bucketed against `rollout_percentage`. Inside the percentage gets `on`, outside gets `default_variant`.

Segments are named rule sets that several flags can share. A segment matches if
any of its rules match, or if the user falls inside the segment's own rollout
percentage.

Bucketing is stable for a given flag and user. Flags created before the salt change carry `bucketing_version = 1` so their existing buckets don't move.

## Context

The SDK sends a context with every evaluation. `user_id` is the only one the
service depends on, it's what bucketing hashes. Everything else is whatever the
caller put in, and rules match against it by name. In practice we get:

```
user_id
account_id     the tenant the user belongs to, sent on every request
plan
email
region
app_version
```

The batch endpoint is called once per account on startup, so a single batch is
always one account's users.

## Layout

```
backend/app/evaluator.py   evaluation and bucketing
backend/app/matchers.py    rule operators
backend/app/api.py         SDK endpoints
backend/app/admin.py       CRUD behind the admin UI
frontend/src/components    admin UI
```

## Endpoints

`POST /api/v1/evaluate` evaluates every flag for one user context.

`POST /api/v1/evaluate/batch` does the same for many contexts at once. The SDK
calls this on startup.

`GET /api/flags/check` is the old single flag endpoint. The 3.x mobile clients
still use it. Nothing new should.

## Running it locally

```
just dev
```

That installs both sides, seeds a SQLite database and brings up the API on
:5000 and the admin UI on :3000. Seed data is three flags with targeting rules
on them.

If those ports are busy, `UI_PORT=3001 API_PORT=5001 just dev`.

`just test` runs the backend tests. They use stubs, so no database is needed.
`just reset` drops the local database.

Production runs on Postgres. Set `DATABASE_URL` to point at it.

## Migrations

Alembic, under `backend/migrations`. The service ran on `create_all` until
2023, so the first revision is a baseline of the schema as it was already
running in prod. Anything that changes the schema needs a revision.

```
cd backend
uv run alembic revision --autogenerate -m "what changed"
uv run alembic upgrade head
```

`just migrate` runs anything pending. Note that `seed.py` still calls
`create_all`, which is convenient locally and will hide a missing revision
until deploy.
