from __future__ import annotations
from fastapi import HTTPException
from ai_real_estate_fund.portfolio import AllocationCandidate, GreedyPortfolioOptimizer, PortfolioConstraints
from ..models.schemas import OptimizeRunsPayload, PortfolioPayload
from ..repositories.analysis_repository import AnalysisRepository


def _risk_score(decision: dict) -> float:
    """Return the dedicated risk agent's score, or fall back to the overall score.

    Mirrors the canonical lookup in investment_committee/orchestrator.py, which
    matches the exact agent name "Risk Manager Agent". A name-substring fallback
    covers committees that label the synthesizing risk agent differently. Match
    on the agent NAME only — many non-risk agents (Debt Capital Markets, Lease-Up,
    Tax, …) mention "risk" in their role *description*, so a name+role match would
    mis-select the first of those instead of the actual risk agent.
    """
    findings = decision.get("findings", []) or []
    for finding in findings:
        if finding.get("agent_name") == "Risk Manager Agent" and finding.get("score") is not None:
            return float(finding["score"])
    for finding in findings:
        if "risk" in str(finding.get("agent_name", "")).lower() and finding.get("score") is not None:
            return float(finding["score"])
    return float(decision.get("overall_score", 0.0))


def _candidate_from_run(decision: dict) -> AllocationCandidate | None:
    """Map a stored decision dict -> AllocationCandidate. Returns None if the run
    is missing required property/metrics fields (so a malformed/old run is skipped)."""
    prop = decision.get("property")
    metrics = decision.get("metrics")
    if not isinstance(prop, dict) or not isinstance(metrics, dict):
        return None
    if "name" not in prop or "market" not in prop:
        return None
    if "cash_invested" not in metrics:
        return None
    return AllocationCandidate(
        name=prop["name"],
        market=prop["market"],
        score=float(decision.get("overall_score", 0.0)),
        risk_score=_risk_score(decision),
        required_equity=float(metrics["cash_invested"]),
        expected_irr=metrics.get("irr"),
        cash_on_cash_return=float(metrics.get("cash_on_cash_return", 0.0)),
        cap_rate=float(metrics.get("cap_rate", 0.0)),
        recommendation=str(decision.get("recommendation", "")),
    )


class PortfolioService:
    def __init__(self, repository: AnalysisRepository | None = None) -> None:
        self.repository = repository or AnalysisRepository()

    def optimize(self, body: PortfolioPayload) -> dict:
        constraints = PortfolioConstraints(total_equity_budget=float(body.total_equity_budget))
        try:
            candidates = [AllocationCandidate(**item) for item in body.candidates]
        except TypeError as exc:
            raise HTTPException(status_code=422, detail=f"invalid allocation candidate: {exc}") from exc
        return GreedyPortfolioOptimizer().optimize(candidates, constraints).to_dict()

    def optimize_from_runs(self, body: OptimizeRunsPayload) -> dict:
        notes: list[str] = []
        if body.run_ids:
            decisions: list[dict] = []
            for run_id in body.run_ids:
                decision = self.repository.get(run_id)
                if decision is None:
                    notes.append(f"Skipped {run_id}: run not found.")
                    continue
                decisions.append(decision)
        else:
            decisions = self.repository.list_recent(100)

        candidates: list[AllocationCandidate] = []
        for decision in decisions:
            candidate = _candidate_from_run(decision)
            if candidate is None:
                notes.append(f"Skipped {decision.get('run_id', '<unknown>')}: missing property/metrics.")
                continue
            candidates.append(candidate)

        constraints = PortfolioConstraints(
            total_equity_budget=float(body.total_equity_budget),
            max_single_asset_pct=float(body.max_single_asset_pct),
            max_market_pct=float(body.max_market_pct),
            min_score=float(body.min_score),
            min_risk_score=float(body.min_risk_score),
            reserve_rate=float(body.reserve_rate),
        )
        plan = GreedyPortfolioOptimizer().optimize(candidates, constraints)
        plan.notes = notes + plan.notes
        return {
            "budget": float(body.total_equity_budget),
            "candidates": [c.to_dict() for c in candidates],
            "plan": plan.to_dict(),
        }
