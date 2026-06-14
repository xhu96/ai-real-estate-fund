# API

Start the backend:

```bash
python -m pip install -e ".[api]"
uvicorn app.backend.main:create_app --factory --reload
```

This runs the API alone on `:8000`. To serve the API and the built SPA from one
process, use `./app/run.sh`; to run the API plus a live-reload Vite dev server,
use `./dev.sh`.

The scope column lists the access scope each route requires via
`require_scope(...)`. In demo/local it is satisfied automatically (see Auth);
in staging/production a valid API key carrying that scope is required.

## Analysis

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/institutional/analyze` | `analyze` | full institutional committee analysis; `?llm=true` adds analyst commentary (optional `llm_provider`/`llm_model`); persists the run |
| `POST` | `/analyses` | `analyze` | run screening committee analysis and persist the result |
| `POST` | `/scenarios` | `analyze` | scenario analysis for a property payload |

## Memo and PDF export

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/institutional/memo.md` | `export` | institutional markdown memo (`text/markdown`) |
| `POST` | `/institutional/report.pdf` | `export` | institutional PDF report (`application/pdf`, attachment) |
| `POST` | `/exports/memo.md` | `export` | screening committee markdown memo (`text/markdown`) |
| `POST` | `/exports/report.pdf` | `export` | screening committee PDF report (`application/pdf`, attachment) |

PDFs are rendered by `src/ai_real_estate_fund/report_pdf.py` (pure-Python via
`fpdf2`), so no system libraries are required.

## Runs and roster

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/analyses` | `read` | list recent analysis runs (`?limit=`, default 25) |
| `GET` | `/analyses/{run_id}` | `read` | fetch a single run by id (404 if unknown) |
| `GET` | `/committee/roster` | `read` | committee agent roster grouped by category, with weights and citations |

## Portfolio

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/portfolio/optimize` | `analyze` | portfolio allocation optimizer over a supplied candidate set |
| `POST` | `/portfolio/optimize-runs` | `analyze` | optimize across saved analysis runs |

## Research and backtest

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/research/backtest` | `analyze` | backtest the screening model against a dataset |

## Comps and validation

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/comps/{market}` | `read` | rent and sale comps for a market |
| `POST` | `/validation/calibration` | `analyze` | calibration metrics from `scores` and `outcomes` |
| `POST` | `/validation/drift` | `analyze` | drift metrics from `expected` and `actual` |

## LLM

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/llm/status` | `read` | resolved provider, whether a server key is present, base URL and default model (no secrets) |
| `GET` | `/llm/models` | `read` | model ids from the provider catalog (`X-LLM-Key`/`X-LLM-Base` override the `.env` key) |
| `POST` | `/llm/test` | `analyze` | fire one tiny completion to confirm credentials and model work end-to-end |

The default model for the `nvidia` provider is `meta/llama-3.1-8b-instruct`.

## Storage, watchlist, and properties

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/storage/status` | `read` | storage backend status |
| `POST` | `/watchlist` | `write` | add a property to the watchlist |
| `GET` | `/properties` | `read` | list saved properties (`?limit=`, default 50) |
| `POST` | `/properties` | `write` | save a property |

## Ops

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/health` | public | legacy health check |
| `GET` | `/ops/health` | public | runtime health checks |
| `GET` | `/ops/ready` | `read` | readiness report (JSON) |
| `GET` | `/ops/ready.md` | `read` | readiness report (markdown) |
| `GET` | `/ops/metrics` | public | Prometheus metrics |
| `GET` | `/ops/config` | `admin` | redacted runtime configuration |
| `GET` | `/ops/audit/verify` | `admin` | audit hash-chain verification |

## Auth

Auth is **open in demo/local and fail-closed in deployed environments**. Every
data and mutating route depends on `require_scope(...)`; only `/health`,
`/ops/health`, and `/ops/metrics` stay open.

Demo mode is fail-open only when all of the following hold (see
`ProductionSettings.allows_demo_mode` in
`src/ai_real_estate_fund/production/settings.py`):
`ENABLE_DEMO_MODE` is on, `REQUIRE_API_KEY` is off, and `APP_ENV` is one of
`development`, `dev`, `local`, `test`, `ci`. In that case requests run as a
`demo` principal with `read`, `write`, `analyze`, and `export` scopes.

Any deployed environment (`staging`, `production`) or an unknown `APP_ENV`
falls through to API-key verification: set `REQUIRE_API_KEY=true` and provide
`API_KEY_HASHES` (or `API_KEYS`), then send the key in the `X-API-Key` header.
A missing or insufficient key returns `401`.

```bash
curl -H "X-API-Key: $AI_REF_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/duplex_sunbelt.json \
  http://localhost:8000/institutional/analyze
```

Use `Idempotency-Key` on `/institutional/analyze` requests that may be retried
by clients.

## Request validation

Routes backed by pydantic models (`/portfolio/*`, `/watchlist`,
`/research/backtest`) reject malformed bodies with `422` rather than `500`.
`parse_property_input` (`app/backend/utils/parsing.py`) maps bad property
payloads to `422` as well. A catch-all error handler
(`app/backend/middleware/errors.py`) returns structured errors without leaking
internal details.
