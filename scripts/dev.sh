#!/usr/bin/env bash
# One-command local demo: API on :8000, frontend on :5173.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -c "import uvicorn, fastapi" 2>/dev/null || {
  echo "Installing API dependencies (one time)..."
  python3 -m pip install -e ".[api]"
}

echo "Starting API on http://localhost:8000 ..."
python3 -m uvicorn app.backend.main:create_app --factory --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null' EXIT

cd app/frontend
[ -d node_modules ] || npm install --no-audit --no-fund
echo
echo "Open http://localhost:5173 — Ctrl+C stops both servers."
npm run dev -- --port 5173
