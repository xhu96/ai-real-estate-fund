from __future__ import annotations
from ai_real_estate_fund.validation import calibration_table, population_stability_index

class ValidationService:
    def calibration(self, scores: list[float], outcomes: list[bool]) -> list[dict[str, float]]:
        return calibration_table(scores, outcomes)

    def drift(self, expected: list[float], actual: list[float]) -> dict[str, float]:
        return {"psi": population_stability_index(expected, actual)}
