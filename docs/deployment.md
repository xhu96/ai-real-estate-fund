# Deployment

## Run modes

Two scripts run the app, and neither needs a copied API URL: the frontend auto-connects.

- `./dev.sh` starts the API (FastAPI/uvicorn on `:8000`) and the Vite dev server with live reload on `:5173`, then open http://localhost:5173. Vite proxies API paths to the backend (`VITE_PROXY_TARGET`/`BACKEND_URL` override, default `:8000`). Best while editing the UI.
- `./app/run.sh` is the single-server mode: it installs the `api` extra, builds the SPA, and serves the built dashboard plus the API from one uvicorn process, then open http://localhost:8000. `HOST` (default `127.0.0.1`) and `PORT` (default `8000`) are configurable, and `SKIP_FRONTEND_BUILD=1` reuses an existing build. Both scripts load `.env` from the repo root first.

In single-server mode `app/backend/main.py` mounts `app/frontend/dist` at `/` only when that build directory exists, so the same code path runs the API alone in dev and tests. `apiBase()` in `app/frontend/src/api/client.ts` is same-origin by default; a manual override (Settings, stored in localStorage) still wins for remote backends.

## Dependencies

PDF reports are rendered server-side by `src/ai_real_estate_fund/report_pdf.py` using `fpdf2` (pure-python, no system libraries). `fpdf2>=2.7` is included in the `api`, `prod`, and `all` extras in `pyproject.toml`. The `dev` extra includes `httpx` for the API test client.

## Docker

```bash
docker compose up --build                                          # local
APP_ENV=production docker compose -f compose.production.yml up     # production-style
```

`compose.production.yml` sets `APP_ENV=production` and `REQUIRE_API_KEY=true` and loads `.env.production`.

## Deployed-environment auth

Auth is fail-closed in deployed environments. `ProductionSettings.allows_demo_mode` (in `src/ai_real_estate_fund/production/settings.py`) is true only when `ENABLE_DEMO_MODE` is on, `REQUIRE_API_KEY` is off, and `APP_ENV` is one of `development`, `dev`, `local`, `test`, or `ci`. Any other environment (including `staging`, `production`, or an unrecognized `APP_ENV`) requires a valid API key.

To run a deployed environment, set:

- `APP_ENV=staging` or `APP_ENV=production`
- `REQUIRE_API_KEY=true`
- `API_KEY_HASHES` (or `API_KEYS`) with key material

Requests then present a key via the `X-API-Key` header, verified by `require_scope(...)` in `app/backend/dependencies.py`. The readiness checker treats production without key material or with `REQUIRE_API_KEY` disabled as a failure.

Every data and mutating route carries a scope dependency. The open endpoints are `/health`, `/ops/health`, and `/ops/metrics`; `/ops/ready` and `/ops/ready.md` require the `read` scope, and `/ops/config` and `/ops/audit/verify` require `admin`. Interactive docs (`/docs`, `/redoc`) are served only in demo mode.

## API endpoints

All paths are mounted by `app/backend/main.py`.

- Health and ops: `GET /health`, `GET /ops/health`, `GET /ops/ready`, `GET /ops/ready.md`, `GET /ops/metrics`, `GET /ops/config`, `GET /ops/audit/verify`
- Analyses: `POST /analyses`, `GET /analyses`, `GET /analyses/{run_id}`
- Institutional: `POST /institutional/analyze`, `POST /institutional/memo.md`, `POST /institutional/report.pdf`
- Exports: `POST /exports/memo.md`, `POST /exports/report.pdf`
- Committee: `GET /committee/roster`
- Portfolio: `POST /portfolio/optimize`, `POST /portfolio/optimize-runs`
- Research: `POST /research/backtest`
- Comps and validation: `GET /comps/{market}`, `POST /validation/calibration`, `POST /validation/drift`
- LLM: `GET /llm/status`, `GET /llm/models`, `POST /llm/test`
- Properties, scenarios, watchlist, storage: `GET /properties`, `POST /properties`, `POST /scenarios`, `POST /watchlist`, `GET /storage/status`

## Production hardening

Production deployment still requires the operational pieces the readiness checker flags: a managed (non-SQLite) database with migrations, explicit (non-wildcard) `CORS_ORIGINS` and `ALLOWED_HOSTS`, a high-entropy `SECRET_KEY`, TLS termination (`REQUIRE_TLS=true`), secrets management, observability, backups, and a security review. Run `APP_ENV=production python -m ai_real_estate_fund readiness --strict` to validate configuration before release.
