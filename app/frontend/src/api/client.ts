import type { CommitteeDecision, InstitutionalDecision, PropertyInput } from '../types';

export function apiBase(): string {
  return localStorage.getItem('aref.apiBase') || import.meta.env.VITE_API_BASE || 'http://localhost:8000';
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase()}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init });
  if (!response.ok) {
    let detail = `${response.status}`;
    try { detail = `${response.status}: ${JSON.stringify(await response.json()).slice(0, 140)}`; } catch { /* keep status */ }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export function analyzeScreening(payload: PropertyInput): Promise<CommitteeDecision> {
  return request('/analyses', { method: 'POST', body: JSON.stringify(payload) });
}

export interface LlmOptions { enabled: boolean; provider?: string; model?: string }

export function analyzeInstitutional(payload: PropertyInput, llm: LlmOptions): Promise<InstitutionalDecision> {
  const params = new URLSearchParams();
  if (llm.enabled) {
    params.set('llm', 'true');
    if (llm.provider) params.set('llm_provider', llm.provider);
    if (llm.model) params.set('llm_model', llm.model);
  }
  const qs = params.toString();
  return request(`/institutional/analyze${qs ? `?${qs}` : ''}`, { method: 'POST', body: JSON.stringify(payload) });
}

export function recentAnalyses(): Promise<CommitteeDecision[]> { return request('/analyses'); }
export function fetchComps(market: string): Promise<Record<string, unknown>> { return request(`/comps/${encodeURIComponent(market)}`); }
