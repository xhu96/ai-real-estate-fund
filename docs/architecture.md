# Architecture

AI Real Estate Fund is split into five layers:

1. **Core engine**: dataclasses, underwriting math, the deterministic workstream committee, policy gates, memo rendering, and a pure-python PDF renderer (`src/ai_real_estate_fund/report_pdf.py`, fpdf2 only).
2. **LLM analyst layer** (optional): four personas, Bull Advocate, Bear Advocate, Risk Officer, IC Chair, debate the committee's structured fact pack through NVIDIA (default), OpenAI, Anthropic, or Gemini, or any OpenAI-compatible endpoint. Analysts run sequentially so the Chair reacts to prior opinions. They attach commentary; they never modify scores. The default NVIDIA model is `meta/llama-3.1-8b-instruct`.
3. **Research layer**: backtesting and historical-deal simulation over the screening committee.
4. **Service layer**: FastAPI routes, service classes, repositories, SQLite persistence, audit log.
5. **Interface layer**: CLI, React dashboard, Docker.

The split is deliberate: numbers come from rules (bit-identical reruns, testable), narrative comes from models (fragile assumptions, sponsor questions), and a model hallucination can never change a score. The fact pack handed to analysts is built only from the decision object, so every claim is checkable against the memo.

## Deterministic vs LLM split

The committee score is fully deterministic. The only place a model is invoked is the analyst commentary layer, which reads the finished decision object and never writes back to it. Recommendation thresholds come from one source of truth, `recommendation_from_score` in `src/ai_real_estate_fund/scenarios.py` (BUY at 78, NEGOTIATE at 66, WATCHLIST at 52), shared by both the institutional and screening paths.

## Config-driven supporting families

Five supporting families under `src/ai_real_estate_fund/institutional/` were collections of dozens of near-identical clone files. Each is now a config-driven registry: a single generic `base.py` plus a `specs.py` that lists the per-instance constants and rebuilds every original class name, so existing imports keep working and behavior is byte-identical (covered by golden-master tests):

- `asset_management/` (`base.py` + `specs.py` + `models.py`): one generic `Monitor` plus a `MonitorSpec` list.
- `research/` (`base.py` + `specs.py`): one `BaseSignal` plus a `SignalSpec` list and `SIGNAL_REGISTRY`.
- `underwriting/` (`base.py` + `specs.py`): one `Model` plus a `ModelSpec` list.
- `integrations/` (`base.py` + `specs.py`): one `Adapter` plus an `AdapterSpec` list and `REGISTRY`.
- `model_validation/` (`base.py` + `specs.py`): one `BaseValidator` plus a `ValidatorSpec` list and `REGISTRY`.

These families are illustrative, uncalibrated deterministic heuristics that demonstrate the shape of a production fund system. They are standalone and are not wired into the committee decision.

## HTTP API

Routers live in `app/backend/routes/` and are mounted in `app/backend/main.py`. Public paths:

- Analysis and memos: `POST /institutional/analyze`, `POST /institutional/memo.md`, `POST /institutional/report.pdf`; `POST /exports/memo.md`, `POST /exports/report.pdf`.
- Saved runs: `POST /analyses`, `GET /analyses`, `GET /analyses/{run_id}`.
- Committee: `GET /committee/roster`.
- Portfolio: `POST /portfolio/optimize`, `POST /portfolio/optimize-runs`.
- Research: `POST /research/backtest`.
- Market and validation tools: `GET /comps/{market}`, `POST /validation/calibration`, `POST /validation/drift`.
- LLM: `GET /llm/status`, `GET /llm/models`, `POST /llm/test`.
- Ops: `GET /ops/health`, `GET /ops/ready`, `GET /ops/ready.md`, `GET /ops/metrics`, `GET /ops/config`, `GET /ops/audit/verify`; plus the bare `GET /health`.
- Other data and mutation: `POST /scenarios`, `POST /watchlist`, `GET /storage/status`, `GET /properties`, `POST /properties`.

PDF reports are produced by `report_pdf.render_report_pdf`, which accepts a screening or institutional decision object or a normalized dict and lays both out through one defensive code path. fpdf2 is declared in the `[api]`, `[prod]`, and `[all]` extras; `httpx` is in `[dev]`.

## Single-server option

There are two ways to run the stack. `./dev.sh` starts the API on `:8000` and Vite on `:5173` with live reload. `./app/run.sh` builds the SPA and serves it together with the API from a single uvicorn process (default `127.0.0.1:8000`; `HOST`/`PORT` configurable, `SKIP_FRONTEND_BUILD=1` to reuse an existing build).

The frontend auto-connects. In dev, `app/frontend/vite.config.ts` proxies the API path prefixes to the backend (`VITE_PROXY_TARGET`/`BACKEND_URL` override, default `:8000`), and `apiBase()` in `app/frontend/src/api/client.ts` is same-origin by default (a manual override saved to localStorage via Settings still wins). In single-server mode, `app/backend/main.py` mounts `app/frontend/dist` at `/` when the build exists; the mount is added after the API routers so they take precedence, and it is skipped when there is no build (dev with Vite, or tests).

## Auth

Authentication is fail-closed in deployed environments. `ProductionSettings.allows_demo_mode` (`src/ai_real_estate_fund/production/settings.py`) is true only when `enable_demo_mode` is set, `require_api_key` is false, and the environment is one of `development`, `dev`, `local`, `test`, or `ci`. `staging` and `production` therefore require a valid API key (`REQUIRE_API_KEY=true` plus `API_KEY_HASHES`). Every data or mutating route carries `Depends(require_scope(...))` (`app/backend/dependencies.py`); `/health`, `/ops/health`, and `/ops/metrics` stay open.

## Request handling

`POST /portfolio/*` and `POST /watchlist` validate input with pydantic models, so bad payloads return 422 rather than 500; `parse_property_input` in `app/backend/utils/parsing.py` maps malformed property payloads to 422 the same way. Logging is configured in `app/backend/logging_config.py`, and a catch-all error handler in `app/backend/middleware/errors.py` returns clean errors without leaking internals.

## Frontend

The dashboard (`app/frontend/src`) is a React + TypeScript + Vite SPA using `HashRouter` (`main.tsx`, `App.tsx`); `react-router-dom` is a dependency. Pages: Overview (Dashboard, `/`), Analyze (`/analyze`, a required-vs-optional form with default placeholders, Import JSON, Download memo `.md`, Download PDF), Runs (`/runs`) and RunDetail (`/runs/:runId`, Export JSON, Download PDF), Committee (`/committee`, roster drill-down by category with weights and citations), Portfolio (`/portfolio`, optimize across saved runs), Research lab (`/research`, backtest), Tools (`/tools`, market comps and model calibration/drift), and Settings (`/settings`). `CommandPalette.tsx` is a Cmd-K search over runs and pages; `src/lib/download.ts` holds the CSV/JSON/Blob export helpers. The design system is neobrutalist (see PRODUCT.md): light saturated-pastel fields, white cards, 2px near-black borders, hard offset shadows, vivid flat verdict fills, Space Grotesk display.
