from __future__ import annotations
from ..models import CommitteeDecision

def decision_to_flat_rows(decision: CommitteeDecision) -> list[dict[str, object]]:
    rows = []
    for finding in decision.findings:
        rows.append({
            "run_id": decision.run_id,
            "property": decision.property.name,
            "agent": finding.agent_name,
            "score": finding.score,
            "recommendation": finding.recommendation.value,
            "confidence": finding.confidence,
            "thesis": finding.thesis,
        })
    return rows
