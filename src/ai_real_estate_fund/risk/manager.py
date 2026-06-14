from __future__ import annotations
from ..models import CommitteeDecision, RiskItem

_SEVERITY = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_PROBABILITY = {"low": 1, "medium": 2, "high": 3}


def risk_score_from_register(risks: list[RiskItem]) -> float:
    if not risks:
        return 100.0
    raw = sum(_SEVERITY.get(r.severity, 2) * _PROBABILITY.get(r.probability, 2) for r in risks)
    return max(0.0, 100 - raw * 4)


class RiskManager:
    def summarize(self, decision: CommitteeDecision) -> dict[str, object]:
        risk_score = risk_score_from_register(decision.risk_register)
        high = [r for r in decision.risk_register if r.severity in {"high", "critical"}]
        return {
            "risk_score": risk_score,
            "high_risk_count": len(high),
            "top_risks": [r.to_dict() for r in decision.risk_register[:5]],
            "can_proceed": risk_score >= 60 and not any(r.severity == "critical" for r in decision.risk_register),
        }
