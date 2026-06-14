# Backend

FastAPI facade over the core `ai_real_estate_fund` package. The backend separates HTTP routes, middleware, persistence, repositories, and services so the core agents remain reusable from CLI, tests, notebooks, or workers.

## Routes

Health and ops:

- `GET /health`
- `GET /ops/health`, `GET /ops/ready`, `GET /ops/ready.md`, `GET /ops/metrics`, `GET /ops/config`, `GET /ops/audit/verify`

Analysis and reporting:

- `POST /institutional/analyze`, `POST /institutional/memo.md`, `POST /institutional/report.pdf`
- `POST /exports/memo.md`, `POST /exports/report.pdf`
- `POST /analyses`, `GET /analyses`, `GET /analyses/{run_id}`
- `GET /committee/roster`

Portfolio, research, and validation:

- `POST /portfolio/optimize`, `POST /portfolio/optimize-runs`
- `POST /research/backtest`
- `GET /comps/{market}`
- `POST /validation/calibration`, `POST /validation/drift`

LLM:

- `GET /llm/status`, `GET /llm/models`, `POST /llm/test`

Data and storage:

- `GET /properties`, `POST /properties`
- `POST /scenarios`, `POST /watchlist`, `GET /storage/status`

PDF reports are rendered by `src/ai_real_estate_fund/report_pdf.py` (fpdf2, pure-python).

## Auth

The API is fail-closed in deployed environments. `require_scope(...)` (see `dependencies.py`) only allows demo (fail-open) access when `ProductionSettings.allows_demo_mode` is true, which requires `ENABLE_DEMO_MODE=true`, `REQUIRE_API_KEY` disabled, and `APP_ENV` in `{development, dev, local, test, ci}`. Staging and production (or any unknown `APP_ENV`) fall through to key verification: set `REQUIRE_API_KEY=true` and supply `API_KEY_HASHES`.

Every data and mutating route carries `Depends(require_scope(...))`. The open endpoints are `GET /health`, `GET /ops/health`, and `GET /ops/metrics`.

Request bodies are validated with pydantic models on `/portfolio`, `/research`, and `/watchlist` (bad input returns 422, not 500); `utils/parsing.py` maps malformed property payloads to 422. A catch-all exception handler (`middleware/errors.py`) normalizes errors without leaking internals; logging is configured in `logging_config.py`.

## Middleware

- request ID
- process timing
- security headers
- request size limit
- audit logging
- exception normalization

## Run

API only (factory app):

```bash
python -m pip install -e ".[api]"
uvicorn app.backend.main:create_app --factory --reload
```

Dev mode (API on :8000 + Vite on :5173 with live reload), from the repo root:

```bash
./dev.sh
```

Single-server mode (build the SPA and serve it + the API from one uvicorn, default :8000):

```bash
./app/run.sh
```

`run.sh` honors `HOST`, `PORT`, and `SKIP_FRONTEND_BUILD=1`. When `app/frontend/dist` exists, `main.py` mounts it at `/` via `StaticFiles` (after the API routers, so routes take precedence). The mount is skipped when there is no build, so dev (Vite) and tests are unaffected.
