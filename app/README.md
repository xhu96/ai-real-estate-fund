# AI Real Estate Fund App

This directory contains an optional full-stack application around the core underwriting package.

- `backend/`: FastAPI service, SQLite/Postgres-style repositories, event schemas, and API routes.
- `frontend/`: Vite + React + TypeScript dashboard for property analysis, runs, committee, comps, and portfolio review.

The app is intentionally optional so the core CLI and tests can run with the Python standard library.

## Run it

Two ways to run, both from the repo root. The frontend auto-connects to the API in both, so there is nothing to configure.

```bash
./dev.sh        # dev: API on :8000 + Vite (live reload) on :5173, then open http://localhost:5173
./app/run.sh    # single server: builds the SPA and serves it + the API, then open http://localhost:8000
```

- `./dev.sh` installs the `[api]` extra, starts uvicorn (`backend.main:create_app --factory --reload`) on :8000, and runs `npm run dev` for Vite on :5173. Use it while editing the UI.
- `./app/run.sh` installs the `[api]` extra, builds the SPA (`npm run build`, skip with `SKIP_FRONTEND_BUILD=1`), and serves it plus the API from one uvicorn process. Defaults to `127.0.0.1:8000`; override with `PORT` and `HOST`.

Both scripts load LLM keys and other settings from a repo-root `.env` if present, so the analyst debate works out of the box.

### How the frontend connects

- Dev: `frontend/vite.config.ts` proxies the API path prefixes (`analyses`, `institutional`, `committee`, `comps`, `llm`, `validation`, `portfolio`, `exports`, `scenarios`, `watchlist`, `ops`, `health`, `research`, `storage`, `properties`) to the backend at `http://localhost:8000`. Override the target with `VITE_PROXY_TARGET` or `BACKEND_URL`.
- Single server: `backend/main.py` mounts `frontend/dist` at `/` when the build exists, so one origin serves both the UI and the API. The mount is skipped when there is no build (dev with Vite, or tests).
- `apiBase()` in `frontend/src/api/client.ts` is same-origin by default. A manual override saved in Settings (localStorage) always wins, for a remote or non-default backend.

## API routes

All routers are registered in `backend/main.py`. Paths and methods:

- Analyses: `POST /analyses`, `GET /analyses`, `GET /analyses/{run_id}`
- Institutional: `POST /institutional/analyze`, `POST /institutional/memo.md`, `POST /institutional/report.pdf`
- Exports: `POST /exports/memo.md`, `POST /exports/report.pdf`
- Committee: `GET /committee/roster`
- Comps: `GET /comps/{market}`
- Portfolio: `POST /portfolio/optimize`, `POST /portfolio/optimize-runs`
- Research: `POST /research/backtest`
- Validation: `POST /validation/calibration`, `POST /validation/drift`
- LLM: `GET /llm/status`, `GET /llm/models`, `POST /llm/test`
- Scenarios / watchlist / properties: `POST /scenarios`, `POST /watchlist`, `GET /properties`, `POST /properties`
- Storage: `GET /storage/status`
- Ops: `GET /ops/health`, `GET /ops/ready`, `GET /ops/ready.md`, `GET /ops/metrics`, `GET /ops/config`, `GET /ops/audit/verify`, plus `GET /health`

PDF reports are generated in `src/ai_real_estate_fund/report_pdf.py` (fpdf2, pure Python; included in the `[api]`, `[prod]`, and `[all]` extras).

## Auth

Auth fails closed in deployed environments (`backend/dependencies.py`, `src/ai_real_estate_fund/production/settings.py`). `ProductionSettings.allows_demo_mode` is true only when `enable_demo_mode` and not `require_api_key` and `environment` is one of `development`, `dev`, `local`, `test`, `ci`. `staging` and `production` require a valid API key (`REQUIRE_API_KEY=true` plus `API_KEY_HASHES`). Every data and mutating route carries `Depends(require_scope(...))`; `/health`, `/ops/health`, and `/ops/metrics` stay open.

Request payloads on `/portfolio` and `/watchlist` are validated with pydantic models so bad input returns 422 rather than 500; `backend/utils/parsing.py` maps malformed property payloads to 422. A catch-all error handler (`backend/middleware/errors.py`) does not leak internals, with structured logging in `backend/logging_config.py`.

## Frontend pages

The SPA uses `HashRouter` (`frontend/src/main.tsx`, `frontend/src/App.tsx`). Pages:

- Overview (`/`, Dashboard)
- Analyze (`/analyze`, AnalyzeProperty): required-vs-optional form with default placeholders, Import JSON, Download memo `.md`, Download PDF
- Runs (`/runs`) and Run detail (`/runs/:runId`): Export JSON, Download PDF
- Committee (`/committee`): roster drill-down by category with weights and citations
- Portfolio (`/portfolio`): optimize across saved runs
- Research lab (`/research`): backtest
- Tools (`/tools`): market comps plus model calibration and drift
- Settings (`/settings`)

`components/CommandPalette.tsx` is a `⌘K` search over runs and pages. `lib/download.ts` holds CSV/JSON/Blob export helpers. The neobrutalist design system is described in `PRODUCT.md`.
