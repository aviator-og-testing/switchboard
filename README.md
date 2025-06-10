# Switchboard

Feature flag service. Backend is Flask and SQLAlchemy, admin UI is React.

## How a flag evaluates

1. If the flag is disabled, everyone gets `default_variant`.
2. Targeting rules are checked in priority order. First match wins and returns that rule's variant.
3. If no rule matches, the user is bucketed against `rollout_percentage`. Inside the percentage gets `on`, outside gets `default_variant`.

Bucketing is stable for a given flag and user. Flags created before the salt change carry `bucketing_version = 1` so their existing buckets don't move.

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
cd backend
uv sync
export DATABASE_URL=sqlite:///switchboard.db SWITCHBOARD_API_KEYS=dev
uv run python seed.py
uv run flask --app app run
```

Then in a second shell:

```
cd frontend
npm install
REACT_APP_API_KEY=dev npm start
```

The admin UI comes up on :3000 and proxies the API to :5000. Seed data is
three flags with a few targeting rules on them.

Production runs on Postgres. Set `DATABASE_URL` to point at it.

Tests are `uv run pytest` from `backend/`. They use stubs, so no database is
needed.
