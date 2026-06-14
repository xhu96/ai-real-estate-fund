from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class PropertyConditionAgent(CommitteeAgent):
    name = "Property Condition Agent"
    role = "Flags age, deferred maintenance, major systems, and inspection-driven capex risk."
    weight = 1.00
    category = "execution"

    def analyze(self, prop, metrics, data, prior_findings):
        age = 0 if prop.year_built is None else max(0, 2026 - prop.year_built)
        age_score = score_range(age, 100, 0, invert=True)
        rehab_ratio = prop.rehab_budget / prop.purchase_price if prop.purchase_price else 0
        rehab_score = score_range(rehab_ratio, 0.30, 0.02, invert=True)
        score = age_score * 0.45 + rehab_score * 0.55
        positives, concerns = [], []
        if age <= 35:
            positives.append("Asset age is not a major negative in the default screen.")
        elif age >= 75:
            concerns.append("Asset age raises major-systems and environmental diligence requirements.")
        if rehab_ratio > 0.20:
            concerns.append(f"Rehab ratio of {pct(rehab_ratio)} suggests meaningful deferred-maintenance risk.")
        return self.finding(score=score, confidence=0.54, thesis=f"Condition screen uses year built {prop.year_built or 'unknown'} and rehab budget {money(prop.rehab_budget)}.", positives=positives, concerns=concerns, evidence=[self.assumption("year_built", prop.year_built), self.assumption("rehab_budget", prop.rehab_budget)], actions=["Order inspection, sewer scope, roof/HVAC review, environmental screen, and contractor bid before close."])
