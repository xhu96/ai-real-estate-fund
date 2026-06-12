from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class RenovationExecutionAgent(CommitteeAgent):
    name = "Renovation Execution Agent"
    role = "Stress-tests rehab budget, schedule, contingency, and execution complexity."
    weight = 1.05
    category = "execution"

    def analyze(self, prop, metrics, data, prior_findings):
        rehab_ratio = prop.rehab_budget / prop.purchase_price if prop.purchase_price else 0.0
        rehab_per_unit = prop.rehab_budget / prop.unit_count if prop.unit_count else prop.rehab_budget
        ratio_score = score_range(rehab_ratio, 0.35, 0.00, invert=True)
        age_penalty = 0
        if prop.year_built and prop.year_built < 1960:
            age_penalty = 8
        score = ratio_score - age_penalty
        positives, concerns = [], []
        if rehab_ratio <= 0.10:
            positives.append(f"Rehab budget is modest at {pct(rehab_ratio)} of purchase price.")
        elif rehab_ratio <= 0.25:
            concerns.append(f"Rehab budget of {money(prop.rehab_budget)} requires detailed scope control.")
        else:
            concerns.append(f"Heavy rehab at {pct(rehab_ratio)} of purchase price creates overrun and delay risk.")
        if prop.year_built and prop.year_built < 1960:
            concerns.append("Pre-1960 asset may need electrical, plumbing, sewer, lead, asbestos, or foundation review.")
        return self.finding(
            score=score,
            confidence=0.60,
            thesis=f"Execution risk is tied to {money(prop.rehab_budget)} rehab budget or {money(rehab_per_unit)} per unit.",
            positives=positives,
            concerns=concerns,
            evidence=[self.assumption("rehab_budget", prop.rehab_budget), self.assumption("year_built", prop.year_built), self.assumption("unit_count", prop.unit_count)],
            actions=["Require contractor walk-through, line-item bid, 10-15% contingency, and draw schedule."],
        )
