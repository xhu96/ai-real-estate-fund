from __future__ import annotations
from .models import AllocationCandidate, PortfolioConstraints


def validate_candidate(candidate: AllocationCandidate, constraints: PortfolioConstraints) -> tuple[bool, str]:
    if candidate.score < constraints.min_score:
        return False, "committee score below minimum"
    if candidate.risk_score < constraints.min_risk_score:
        return False, "risk score below minimum"
    if candidate.required_equity <= 0:
        return False, "required equity must be positive"
    if candidate.required_equity > constraints.total_equity_budget * constraints.max_single_asset_pct:
        return False, "single-asset concentration exceeds limit"
    if candidate.recommendation == "PASS":
        return False, "committee recommendation is PASS"
    return True, "eligible"
