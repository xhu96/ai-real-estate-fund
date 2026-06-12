from __future__ import annotations
from ai_real_estate_fund.portfolio import AllocationCandidate, GreedyPortfolioOptimizer, PortfolioConstraints

class PortfolioService:
    def optimize(self, payload: dict) -> dict:
        constraints = PortfolioConstraints(total_equity_budget=float(payload["total_equity_budget"]))
        candidates = [AllocationCandidate(**item) for item in payload.get("candidates", [])]
        return GreedyPortfolioOptimizer().optimize(candidates, constraints).to_dict()
