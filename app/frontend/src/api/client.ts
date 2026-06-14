import type { BacktestResult, CalibrationBin, CommitteeDecision, CommitteeRoster, CompsResult, DriftResult, InstitutionalDecision, PortfolioOptimizeResult, PropertyInput } from '../types';

export const DEFAULT_API_BASE = 'http://localhost:8000';

/** True only for an absolute http(s) URL — guards against an API key pasted into the base field. */
export function isApiBaseValid(value: string): boolean {
  return /^https?:\/\/.+/i.test(value.trim());
}

/**
 * Resolve the API base. Priority:
 *  1. Manual override saved in Settings (localStorage) — always wins, for a remote
 *     or non-default backend. This is the "emergency" escape hatch.
 *  2. A build-time VITE_API_BASE.
 *  3. Auto: same-origin (empty base). In dev the Vite proxy forwards API paths to the
 *     backend (default :8000), and a same-origin deploy serves both — so no URL to copy.
 *  4. Production-standalone fallback to the localhost default (prior behavior).
 */
export function apiBase(): string {
  const stored = (localStorage.getItem('aref.apiBase') || '').trim();
  if (stored && isApiBaseValid(stored)) return stored.replace(/\/+$/, '');
  const envBase = ((import.meta.env.VITE_API_BASE as string | undefined) || '').trim();
  if (envBase && isApiBaseValid(envBase)) return envBase.replace(/\/+$/, '');
  // Same-origin: the Vite dev proxy forwards to the backend in dev, and the backend
  // serves this built SPA in production (./app/run.sh). Nothing to configure.
  return '';
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const base = apiBase();
  const url = `${base}${path}`;
  let response: Response;
  try {
    response = await fetch(url, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> | undefined) } });
  } catch {
    const where = base ? `at ${base}` : 'via the dev proxy';
    throw new Error(`Couldn't reach the API ${where}. Is the backend running? Start both with ./dev.sh, or set a backend URL in Settings.`);
  }
  if (!response.ok) {
    let detail = '';
    try { detail = JSON.stringify(await response.json()).slice(0, 200); } catch { /* keep status only */ }
    if (response.status === 404) {
      throw new Error(`Not found (404) at ${url}. Check the API base URL in Settings — it should be ${DEFAULT_API_BASE}, not an API key.`);
    }
    throw new Error(`API error ${response.status} ${response.statusText}${detail ? ` — ${detail}` : ''}`);
  }
  return response.json() as Promise<T>;
}

/** Like request<T>(), but returns the raw response body as text (for text/markdown endpoints). */
async function requestText(path: string, init?: RequestInit): Promise<string> {
  const base = apiBase();
  const url = `${base}${path}`;
  let response: Response;
  try {
    response = await fetch(url, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> | undefined) } });
  } catch {
    const where = base ? `at ${base}` : 'via the dev proxy';
    throw new Error(`Couldn't reach the API ${where}. Is the backend running? Start both with ./dev.sh, or set a backend URL in Settings.`);
  }
  if (!response.ok) {
    let detail = '';
    try { detail = JSON.stringify(await response.json()).slice(0, 200); } catch { /* keep status only */ }
    if (response.status === 404) {
      throw new Error(`Not found (404) at ${url}. Check the API base URL in Settings — it should be ${DEFAULT_API_BASE}, not an API key.`);
    }
    throw new Error(`API error ${response.status} ${response.statusText}${detail ? ` — ${detail}` : ''}`);
  }
  return response.text();
}

/** Like request<T>(), but returns the raw response body as a Blob (for binary endpoints like PDF). */
async function requestBlob(path: string, init?: RequestInit): Promise<Blob> {
  const base = apiBase();
  const url = `${base}${path}`;
  let response: Response;
  try {
    response = await fetch(url, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> | undefined) } });
  } catch {
    const where = base ? `at ${base}` : 'via the dev proxy';
    throw new Error(`Couldn't reach the API ${where}. Is the backend running? Start both with ./dev.sh, or set a backend URL in Settings.`);
  }
  if (!response.ok) {
    let detail = '';
    try { detail = JSON.stringify(await response.json()).slice(0, 200); } catch { /* keep status only */ }
    if (response.status === 404) {
      throw new Error(`Not found (404) at ${url}. Check the API base URL in Settings — it should be ${DEFAULT_API_BASE}, not an API key.`);
    }
    throw new Error(`API error ${response.status} ${response.statusText}${detail ? ` — ${detail}` : ''}`);
  }
  return response.blob();
}

/** Optional per-request LLM overrides → custom headers (blank fields fall back to the server .env). */
function llmHeaders(o?: { apiKey?: string; baseUrl?: string }): Record<string, string> {
  const h: Record<string, string> = {};
  if (o?.apiKey && o.apiKey.trim()) h['X-LLM-Key'] = o.apiKey.trim();
  if (o?.baseUrl && o.baseUrl.trim()) h['X-LLM-Base'] = o.baseUrl.trim();
  return h;
}

export function analyzeScreening(payload: PropertyInput): Promise<CommitteeDecision> {
  return request('/analyses', { method: 'POST', body: JSON.stringify(payload) });
}

export interface LlmOptions { enabled: boolean; provider?: string; model?: string; apiKey?: string; baseUrl?: string }

export function analyzeInstitutional(payload: PropertyInput, llm: LlmOptions): Promise<InstitutionalDecision> {
  const params = new URLSearchParams();
  if (llm.enabled) {
    params.set('llm', 'true');
    if (llm.provider) params.set('llm_provider', llm.provider);
    if (llm.model) params.set('llm_model', llm.model);
  }
  const qs = params.toString();
  return request(`/institutional/analyze${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: llm.enabled ? llmHeaders(llm) : undefined,
  });
}

/** Institutional memo as markdown — mirrors analyzeInstitutional's query/header building so the export matches what's on screen. */
export function exportInstitutionalMemo(payload: PropertyInput, llm: LlmOptions): Promise<string> {
  const params = new URLSearchParams();
  if (llm.enabled) {
    params.set('llm', 'true');
    if (llm.provider) params.set('llm_provider', llm.provider);
    if (llm.model) params.set('llm_model', llm.model);
  }
  const qs = params.toString();
  return requestText(`/institutional/memo.md${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: llm.enabled ? llmHeaders(llm) : undefined,
  });
}

/** Screening memo as markdown — no auth, no LLM options. */
export function exportScreeningMemo(payload: PropertyInput): Promise<string> {
  return requestText('/exports/memo.md', { method: 'POST', body: JSON.stringify(payload) });
}

/**
 * Institutional report as a real PDF (POST /institutional/report.pdf).
 * Mirrors analyzeInstitutional / exportInstitutionalMemo: same llm query params + headers,
 * so the download matches what's on screen. Returns the PDF bytes as a Blob. Auth: export scope
 * (passes in demo/dev; production fails closed with 401).
 */
export function downloadInstitutionalReportPdf(payload: PropertyInput, llm: LlmOptions): Promise<Blob> {
  const params = new URLSearchParams();
  if (llm.enabled) {
    params.set('llm', 'true');
    if (llm.provider) params.set('llm_provider', llm.provider);
    if (llm.model) params.set('llm_model', llm.model);
  }
  const qs = params.toString();
  return requestBlob(`/institutional/report.pdf${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: llm.enabled ? llmHeaders(llm) : undefined,
  });
}

/** Screening report as a real PDF (POST /exports/report.pdf) — no LLM options, mirrors exportScreeningMemo. */
export function downloadScreeningReportPdf(payload: PropertyInput): Promise<Blob> {
  return requestBlob('/exports/report.pdf', { method: 'POST', body: JSON.stringify(payload) });
}

export function recentAnalyses(): Promise<CommitteeDecision[]> { return request('/analyses'); }

// ---- Committee roster (GET /committee/roster) ----
/** The full roster of 77 deterministic diligence workstreams, grouped into the 8 canonical categories. */
export function getRoster(): Promise<CommitteeRoster> { return request('/committee/roster'); }

/**
 * Fetch one persisted run by id (GET /analyses/{run_id}). The backend returns the full decision
 * dict — screening or institutional — so callers detect the kind via `engine`/`scorecards`.
 * A 404 surfaces as the "Not found" error thrown by request().
 */
export function getRun(runId: string): Promise<CommitteeDecision | InstitutionalDecision> {
  return request(`/analyses/${encodeURIComponent(runId)}`);
}
// ---- Market comps (GET /comps/{market}) ----
/** Look up rent and sale comps for a market. An unknown market yields empty arrays. */
export function fetchComps(market: string): Promise<CompsResult> {
  return request(`/comps/${encodeURIComponent(market)}`);
}

// ---- Model validation ----
/** Bin model scores (0–100) against realized boolean outcomes into a reliability table. */
export function runCalibration(scores: number[], outcomes: boolean[]): Promise<CalibrationBin[]> {
  return request('/validation/calibration', { method: 'POST', body: JSON.stringify({ scores, outcomes }) });
}

/** Population Stability Index between an expected and an actual distribution. */
export function runDrift(expected: number[], actual: number[]): Promise<DriftResult> {
  return request('/validation/drift', { method: 'POST', body: JSON.stringify({ expected, actual }) });
}

// ---- Portfolio optimizer (POST /portfolio/optimize-runs) ----
export interface OptimizeRunsBody {
  total_equity_budget: number;
  run_ids?: string[];
  max_single_asset_pct?: number;
  max_market_pct?: number;
  min_score?: number;
  min_risk_score?: number;
  reserve_rate?: number;
}

/** Size an allocation plan across recent runs under concentration + score constraints. */
export function optimizeRuns(body: OptimizeRunsBody): Promise<PortfolioOptimizeResult> {
  return request('/portfolio/optimize-runs', { method: 'POST', body: JSON.stringify(body) });
}

// ---- Research backtest (POST /research/backtest) ----
export interface BacktestBody {
  min_score?: number;
  starting_equity?: number;
  max_positions?: number;
  allocation_per_deal?: number;
}

/** Replay the screening committee over the historical deal panel and report realized vs. modeled outcomes. */
export function runBacktest(body: BacktestBody): Promise<BacktestResult> {
  return request('/research/backtest', { method: 'POST', body: JSON.stringify(body) });
}

// ---- LLM provider configuration (GUI) ----
export interface LlmStatus { provider: string; key_present: boolean; base_url: string; model: string; providers: string[] }

export function llmStatus(provider?: string): Promise<LlmStatus> {
  return request(`/llm/status${provider ? `?provider=${encodeURIComponent(provider)}` : ''}`);
}

export function listModels(opts: { provider?: string; apiKey?: string; baseUrl?: string }): Promise<{ provider: string; count: number; models: string[] }> {
  const qs = opts.provider ? `?provider=${encodeURIComponent(opts.provider)}` : '';
  return request(`/llm/models${qs}`, { headers: llmHeaders(opts) });
}

export function testLlm(opts: { provider?: string; model?: string; apiKey?: string; baseUrl?: string }): Promise<{ ok: boolean; model: string; latency_ms: number; sample: string }> {
  const params = new URLSearchParams();
  if (opts.provider) params.set('provider', opts.provider);
  if (opts.model) params.set('model', opts.model);
  const qs = params.toString();
  return request(`/llm/test${qs ? `?${qs}` : ''}`, { method: 'POST', headers: llmHeaders(opts) });
}
