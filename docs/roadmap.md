# Roadmap

## Shipped

- **Saved runs and deep-linking.** Institutional and screening analyses persist to SQLite (`POST /analyses`, `GET /analyses`, `GET /analyses/{run_id}`) and surface in the dashboard. The Runs page lists recent runs and `RunDetail` (`/runs/:runId`) deep-links a single decision with Export JSON and Download PDF.
- **Committee roster.** `GET /committee/roster` returns the 77 workstreams grouped into eight categories (weights, focus components, report language, and `sources` citations). The Committee page drills down by category.
- **Portfolio optimizer across runs.** `POST /portfolio/optimize` (ad-hoc candidates) and `POST /portfolio/optimize-runs` (optimize across saved runs) back the Portfolio page.
- **Backtesting endpoint and page.** `POST /research/backtest` replays the screening committee over the bundled example deal panel; the Research lab page drives it.
- **Standalone tools.** `GET /comps/{market}` (market comps) and `POST /validation/calibration` / `POST /validation/drift` (calibration table, population stability index) back the Tools page.
- **PDF and Markdown reports.** `src/ai_real_estate_fund/report_pdf.py` renders committee decisions with fpdf2 (pure-python, no system dependencies). Exposed via `POST /institutional/report.pdf`, `POST /institutional/memo.md`, `POST /exports/report.pdf`, and `POST /exports/memo.md`. The Analyze and Run detail pages download both.
- **Model-risk governance.** Calibration tables, assumption-drift (PSI) checks, and a model-risk evaluation attached to every institutional decision (`evaluate_decision_payload`). Operational readiness via `GET /ops/health`, `GET /ops/ready`, `GET /ops/metrics`, `GET /ops/config`, and `GET /ops/audit/verify`.
- **Fail-closed auth.** API-key scopes are enforced in deployed environments; demo mode is allowed only in development/test/CI when `enable_demo_mode` is set and `require_api_key` is off. Every data and mutating route carries a scope dependency; `/health`, `/ops/health`, and `/ops/metrics` stay open.
- **Dashboard.** A React/Vite SPA (HashRouter) covering Overview, Analyze (required-vs-optional form, JSON import, memo and PDF download), Runs and Run detail, Committee, Portfolio, Research lab, Tools, and Settings, plus a ⌘K command palette over runs and pages, CSV/JSON/Blob export helpers, and a neobrutalist design system (see PRODUCT.md).
- **Single-server mode.** `./app/run.sh` builds the SPA and serves it plus the API from one uvicorn process (`backend.main` mounts `app/frontend/dist` at `/` when present); `./dev.sh` runs the API and Vite with live reload. The frontend auto-connects same-origin (Vite proxies API prefixes in dev).
- **Spec consolidation.** The asset-management, research-signal, underwriting-model, integration-adapter, and model-validation families are each a `base.py` + `specs.py` registry (config-driven), with byte-identical behavior verified by golden-master tests. They remain illustrative, uncalibrated heuristics and are not wired into the committee score.

## Next

- **Knowledge-grounded workstreams** *(in progress — 60 of 77 cited at chapter level, see docs/sources.md)*: extend `sources` coverage to all 77 specs and align numeric scoring bands with the cited thresholds (e.g., score debt workstreams against the Fannie 1.25x / HUD 1.15x DSCR floors explicitly).
- Replace fixture data with permissioned property, comp, insurance, and debt feeds.
- Property-level document ingestion (leases, inspection PDFs, tax bills, rent rolls) feeding the data room and the analyst fact pack.
- Richer analyst debate: configurable personas, multi-round rebuttals, and evidence IDs linking commentary to scored findings.
- App authentication and user-specific saved runs (runs currently persist globally, not per user).
- Expand backtesting with real historical acquisitions and market vintages (the current panel is bundled example data); richer example panels.
