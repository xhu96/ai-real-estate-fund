from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.models import PropertyInput


@dataclass(slots=True)
class InstitutionalService:
    """Thin application service for running institutional diligence from an API layer."""

    def analyze_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        prop = PropertyInput.from_dict(payload)
        decision = run_institutional_committee(prop)
        return decision.to_dict()

    def summarize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = self.analyze_payload(payload)
        return {
            "run_id": result["run_id"],
            "property_name": result["property"]["name"],
            "recommendation": result["recommendation"],
            "overall_score": result["overall_score"],
            "hard_stops": result["hard_stops"],
            "next_steps": result["next_steps"][:5],
        }

