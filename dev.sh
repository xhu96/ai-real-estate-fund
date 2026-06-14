#!/usr/bin/env bash
# Start the API (FastAPI, :8000) and the web app (Vite, :5173) together.
# Usage:  ./dev.sh     then open http://localhost:5173
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$ROOT/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
fi

cleanup() { kill 0 2>/dev/null; }
trap cleanup EXIT INT TERM

echo "→ starting backend on http://localhost:8000"
(
  cd "$ROOT/app"
  if [ -f ../.env ]; then set -a; . ../.env; set +a; fi
  python -m pip install -e "..[api]" >/tmp/aref-pip.log 2>&1 || { echo "backend deps install failed — see /tmp/aref-pip.log"; cat /tmp/aref-pip.log; exit 1; }
  exec uvicorn backend.main:create_app --factory --reload --app-dir .
) &

echo "→ starting frontend on http://localhost:5173"
(
  cd "$ROOT/app/frontend"
  if [ ! -d node_modules ]; then npm install; fi
  exec npm run dev
) &

wait
