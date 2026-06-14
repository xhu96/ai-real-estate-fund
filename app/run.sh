#!/usr/bin/env bash
# One server, one URL: build the SPA and let the API serve it same-origin.
# Open http://localhost:8000 — no separate frontend, no API-base to configure.
# (For live frontend HMR while developing, use ../dev.sh instead.)
set -euo pipefail
cd "$(dirname "$0")"
# Load repo-root .env (LLM keys, CORS, etc.) so the analyst debate works out of the box.
if [ -f ../.env ]; then set -a; . ../.env; set +a; fi
python -m pip install -e "..[api]"
# Build the frontend so the API can serve it (skip with SKIP_FRONTEND_BUILD=1).
if [ -z "${SKIP_FRONTEND_BUILD:-}" ]; then
  ( cd frontend && { [ -d node_modules ] || npm ci; } && npm run build )
fi
exec uvicorn backend.main:create_app --factory --app-dir . --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"
