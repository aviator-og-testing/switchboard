api_port := env_var_or_default("API_PORT", "5000")
ui_port := env_var_or_default("UI_PORT", "3000")

export BROWSER := "none"
export DATABASE_URL := "sqlite:///switchboard.db"
export SWITCHBOARD_API_KEYS := "dev"
export REACT_APP_API_KEY := "dev"
export API_PORT := api_port

default:
    @just --list

# install everything, migrate and seed the database
setup:
    cd backend && uv sync
    cd frontend && npm install
    cd backend && uv run alembic upgrade head
    cd backend && uv run python seed.py

# run pending migrations
migrate:
    cd backend && uv run alembic upgrade head

# api and admin ui together
dev: setup
    #!/usr/bin/env bash
    set -euo pipefail
    cd {{ justfile_directory() }}/backend
    uv run flask --app app run --port {{ api_port }} &
    API=$!
    trap 'kill $API 2>/dev/null || true' EXIT
    cd {{ justfile_directory() }}/frontend
    PORT={{ ui_port }} npm start

# api only
api:
    cd backend && uv run flask --app app run --port {{ api_port }}

# admin ui only
ui:
    cd frontend && PORT={{ ui_port }} npm start

test:
    cd backend && uv run pytest

# drop the local database
reset:
    rm -f backend/switchboard.db
