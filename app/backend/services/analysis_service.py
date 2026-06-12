from __future__ import annotations
from ai_real_estate_fund.investment_committee import run_property_committee
from ai_real_estate_fund.models import PropertyInput
from ..repositories.analysis_repository import AnalysisRepository

class AnalysisService:
    def __init__(self, repository: AnalysisRepository | None = None) -> None:
        self.repository = repository or AnalysisRepository()

    def analyze(self, payload: dict, save: bool = True) -> dict:
        payload = dict(payload)
        assumptions = payload.pop("assumptions", {}) if "assumptions" in payload else {}
        prop = PropertyInput.from_dict({**payload, **assumptions})
        decision = run_property_committee(prop).to_dict()
        if save:
            self.repository.save(decision)
        return decision
