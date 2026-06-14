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

// ---- Committee roster (GET /committee/roster) ----
/** One deterministic, config-driven diligence workstream. `weight` sets its pull on the blended score. */
export interface RosterAgent {
  name: string;
  weight: number;
  role: string;
  focus_components: string[];
  positive: string;
  concern: string;
  action: string;
  sources: string[];
}
/** One of the 8 canonical diligence categories, with its ordered agents. */
export interface RosterCategory {
  key: string;
  label: string;
  count: number;
  agents: RosterAgent[];
}
/** The full 77-workstream committee roster grouped by category. */
export interface CommitteeRoster {
  total: number;
  categories: RosterCategory[];
}

// ---- Portfolio optimizer (POST /portfolio/optimize-runs) ----
export interface AllocationCandidate {
  name: string;
  market: string;
  score: number;
  risk_score: number;
  required_equity: number;
  expected_irr: number | null;
  cash_on_cash_return: number;
  cap_rate: number;
  recommendation: Recommendation;
}
export interface PortfolioPlan {
  selected: AllocationCandidate[];
  rejected: AllocationCandidate[];
  equity_used: number;
  reserves: number;
  notes: string[];
}
export interface PortfolioOptimizeResult {
  budget: number;
  candidates: AllocationCandidate[];
  plan: PortfolioPlan;
}

// ---- Market comps (GET /comps/{market}) ----
/** Fields shared by every comp the backend serializes (RentComp / SaleComp via asdict). */
export interface Comp {
  address: string;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  unit_count: number;
  distance_miles: number;
  source: string;
  confidence: number;
  notes: string;
}
/** Rent comp — carries a monthly_rent figure. */
export interface RentComp extends Comp { monthly_rent: number; }
/** Sale comp — carries a sale_price (and sale_date) figure. */
export interface SaleComp extends Comp { sale_price: number; sale_date: string; }
export interface CompsResult { rent_comps: RentComp[]; sale_comps: SaleComp[]; }

// ---- Model validation (POST /validation/calibration, POST /validation/drift) ----
/** One reliability bin: scores in [low, high) and the realized success rate (0–1) within it. */
export interface CalibrationBin { low: number; high: number; count: number; success_rate: number; }
/** Population Stability Index between an expected and an actual distribution. */
export interface DriftResult { psi: number; }

// ---- Research backtest (POST /research/backtest) ----
export interface BacktestTrade {
  deal_name: string;
  selected: boolean;
  score: number;
  recommendation: Recommendation;
  expected_irr: number | null;
  realized_irr: number;
  realized_equity_multiple: number;
}
export interface BacktestResult {
  trades: BacktestTrade[];
  selected_count: number;
  hit_rate: number;
  average_realized_irr: number;
  average_model_score: number;
  ending_equity: number;
}
