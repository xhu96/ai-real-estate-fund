from __future__ import annotations
from ai_real_estate_fund.investment_committee import run_property_committee
from ..repositories.analysis_repository import AnalysisRepository
from ..utils.parsing import parse_property_input

class AnalysisService:
    def __init__(self, repository: AnalysisRepository | None = None) -> None:
        self.repository = repository or AnalysisRepository()

    def analyze(self, payload: dict, save: bool = True) -> dict:
        payload = dict(payload)
        assumptions = payload.pop("assumptions", {}) if "assumptions" in payload else {}
        prop = parse_property_input({**payload, **assumptions})
        decision = run_property_committee(prop).to_dict()
        decision["engine"] = "screening"
        if save:
            self.repository.save(decision)
        return decision
