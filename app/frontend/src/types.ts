export type Recommendation = 'BUY' | 'NEGOTIATE' | 'WATCHLIST' | 'PASS';
export interface PropertyInput { name: string; address: string; market: string; purchase_price: number; monthly_rent: number; unit_count?: number; square_feet?: number; loan_amount?: number; annual_interest_rate?: number; }
export interface AgentFinding { agent_name: string; role: string; score: number; recommendation: Recommendation; confidence: number; thesis: string; positives: string[]; concerns: string[]; }
export interface CommitteeDecision { run_id: string; recommendation: Recommendation; overall_score: number; suggested_allocation_pct: number; property: PropertyInput; findings: AgentFinding[]; scenarios: Array<Record<string, unknown>>; risk_register: Array<Record<string, unknown>>; metrics: Record<string, number>; }

export interface AnalystOpinion { analyst: string; thesis: string; key_points: string[]; questions: string[] }
export interface LlmReview { model: string; generated_at: string; opinions: AnalystOpinion[]; errors: string[] }
export interface PolicyResult { limit: { name: string; severity?: string; description?: string }; value: number; passed: boolean; message: string; remediation?: string }
export interface InstitutionalDecision {
  run_id: string; recommendation: Recommendation; overall_score: number;
  property: PropertyInput; findings: AgentFinding[];
  scenarios: Array<Record<string, unknown>>; risk_register: Array<Record<string, unknown>>;
  metrics: Record<string, number | null>; scorecards: Array<Record<string, unknown>>;
  policy_results: PolicyResult[]; hard_stops: Array<Record<string, unknown>>;
  thesis: string; bear_case: string; next_steps: string[];
  llm_review: LlmReview | null;
}
