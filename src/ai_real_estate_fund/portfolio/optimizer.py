from __future__ import annotations
from collections import defaultdict
from .constraints import validate_candidate
from .models import AllocationCandidate, PortfolioConstraints, PortfolioPlan


def _candidate_rank(candidate: AllocationCandidate) -> tuple[float, float, float]:
    irr = candidate.expected_irr or 0.0
    return (candidate.score + candidate.risk_score, irr, candidate.cash_on_cash_return)


class GreedyPortfolioOptimizer:
    def optimize(self, candidates: list[AllocationCandidate], constraints: PortfolioConstraints) -> PortfolioPlan:
        plan = PortfolioPlan()
        market_equity = defaultdict(float)
        available = constraints.total_equity_budget
        for candidate in sorted(candidates, key=_candidate_rank, reverse=True):
            eligible, reason = validate_candidate(candidate, constraints)
            if not eligible:
                plan.rejected.append(candidate)
                plan.notes.append(f"Rejected {candidate.name}: {reason}.")
                continue
            market_limit = constraints.total_equity_budget * constraints.max_market_pct
            if market_equity[candidate.market] + candidate.required_equity > market_limit:
                plan.rejected.append(candidate)
                plan.notes.append(f"Rejected {candidate.name}: market concentration limit.")
                continue
            if candidate.required_equity > available:
                plan.rejected.append(candidate)
                plan.notes.append(f"Rejected {candidate.name}: insufficient remaining equity.")
                continue
            plan.selected.append(candidate)
            plan.equity_used += candidate.required_equity
            market_equity[candidate.market] += candidate.required_equity
            available -= candidate.required_equity
        plan.reserves = plan.equity_used * constraints.reserve_rate
        return plan
