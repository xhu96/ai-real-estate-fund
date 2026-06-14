# Frontend

A React + Vite single-page dashboard for the diligence engine, under `app/frontend`. It covers the full workflow: analyze a deal, browse and deep-link into saved runs, inspect the committee roster, optimize a portfolio across runs, backtest, and run standalone tools.

## Routing

The app uses `HashRouter` (`src/main.tsx`), so every page is a fragment route and the SPA serves cleanly from any host without server rewrites. Routes are declared in `src/App.tsx`, all wrapped in `Layout`:

- `/` Overview (`pages/Dashboard.tsx`)
- `/analyze` Analyze deal (`pages/AnalyzeProperty.tsx`)
- `/runs` Runs (`pages/Runs.tsx`) and `/runs/:runId` Run detail (`pages/RunDetail.tsx`)
- `/committee` Committee roster (`pages/Committee.tsx`)
- `/portfolio` Portfolio optimizer (`pages/Portfolio.tsx`)
- `/research` Research lab (`pages/ResearchLab.tsx`)
- `/tools` Tools (`pages/Tools.tsx`)
- `/settings` Settings (`pages/Settings.tsx`)

The sidebar nav lives in `components/Layout.tsx`.

## Pages

- **Overview.** Landing dashboard.
- **Analyze deal.** Drives `PropertyForm` and renders the result. After a run it offers Download memo (.md) and Download PDF. The screening committee posts to `POST /analyses`; the institutional committee posts to `POST /institutional/analyze` and can add the LLM analyst debate (bull / bear / risk / chair).
- **Runs / Run detail.** `Runs` lists persisted runs (`GET /analyses`) with an Export CSV button. `RunDetail` loads one run (`GET /analyses/{run_id}`), shows a not-found empty state on 404, and offers Export JSON and Download PDF.
- **Committee.** Drills into the roster by category (`GET /committee/roster`), with per-agent weights, supports/concern/action, and citations.
- **Portfolio.** Sizes an allocation plan across saved runs (`POST /portfolio/optimize-runs`) under concentration and score constraints.
- **Research lab.** Replays the screening committee over the historical panel (`POST /research/backtest`).
- **Tools.** Market comps (`GET /comps/{market}`) plus model calibration (`POST /validation/calibration`) and drift (`POST /validation/drift`).
- **Settings.** Manual API base override plus LLM provider configuration (`GET /llm/status`, `GET /llm/models`, `POST /llm/test`).

## Command palette (⌘K)

`components/CommandPalette.tsx` is a ⌘K / Ctrl+K palette opened from anywhere by the global key handler in `Layout.tsx` (or the appbar search button). It is a native `<dialog>` showmodal with focus trap and Escape-to-close, and searches across the eight pages and recent runs (`GET /analyses`). Arrow keys move the cursor; Enter opens the page or navigates to `/runs/{run_id}`.

## Missing-data form

`components/PropertyForm.tsx` treats most fields as optional. Only name, address, market, and purchase price are required; everything else shows its model default as a grey placeholder and is omitted from the payload when left blank, so the backend default applies. Buttons: Run committee, Reset to example, and Import JSON. Import reads a JSON object, keeps only known field keys, drops unknown keys (so a run will not 422), and merges the values into the form.

## Import / export

`src/lib/download.ts` holds dependency-free helpers: `downloadBlob` (string or Blob), `downloadJSON` (pretty-printed), and `downloadCSV` / `toCSV` (RFC-4180 quoting, union-of-keys header, CRLF lines).

- **Import JSON** into the Analyze form (`PropertyForm`).
- **Export CSV** of saved runs (Runs page).
- **Export JSON** of a single run (Run detail).
- **Download memo (.md):** screening via `POST /exports/memo.md`, institutional via `POST /institutional/memo.md`.
- **Download PDF:** screening via `POST /exports/report.pdf`, institutional via `POST /institutional/report.pdf`. PDFs are real documents rendered server-side by `src/ai_real_estate_fund/report_pdf.py` (fpdf2, pure Python) and fetched as a Blob.

## Design

Neobrutalist and numerate: saturated-pastel fields (cyan content, yellow sidebar), white data cards in 2px near-black borders with hard offset shadows, vivid flat verdict fills, and Space Grotesk display type. The full design system is documented in [PRODUCT.md](../PRODUCT.md). Styles live in `src/styles.css`.

## How it connects

The frontend **auto-connects**, so there is normally no URL to copy. `apiBase()` in `src/api/client.ts` resolves, in priority order: a manual override saved in Settings (`localStorage` key `aref.apiBase`), a build-time `VITE_API_BASE`, then same-origin (an empty base). Same-origin works two ways:

- **Dev (`./dev.sh`):** the API runs on `:8000` and Vite on `:5173` with live reload. `vite.config.ts` proxies the backend path prefixes (analyses, institutional, committee, comps, llm, validation, portfolio, exports, scenarios, watchlist, ops, health, research, storage, properties) to the backend. Override the target with `VITE_PROXY_TARGET` or `BACKEND_URL` (default `http://localhost:8000`).
- **Single server (`./app/run.sh`):** builds the SPA and serves it plus the API from one uvicorn (default `:8000`; `PORT` / `HOST` configurable; `SKIP_FRONTEND_BUILD=1` to reuse a build). The backend mounts `app/frontend/dist` at `/` when it exists.

To point at a different or remote backend, set a full URL in **Settings -> API base URL** (for example `http://localhost:8000`). This manual override always wins. The field validates that the value is an http(s) URL, not an API key.

## Develop

```bash
cd app/frontend
npm install
npm run dev      # Vite dev server on :5173 (needs the API; ./dev.sh starts both)
npm run build    # type-check + bundle to app/frontend/dist
```

Dependencies: React 18, `react-router-dom`, `recharts`, and `lucide-react`.
