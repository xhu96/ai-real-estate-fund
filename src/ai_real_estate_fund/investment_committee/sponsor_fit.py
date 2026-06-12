from __future__ import annotations
from .base import CommitteeAgent, average_prior

class SponsorFitAgent(CommitteeAgent):
    name = "Sponsor Fit Agent"
    role = "Evaluates whether the deal complexity matches the operator's implied execution capacity."
    weight = 0.65
    category = "execution"

    def analyze(self, prop, metrics, data, prior_findings):
        complexity = 0
        if prop.unit_count >= 4: complexity += 12
        if prop.rehab_budget / prop.purchase_price > 0.15: complexity += 18
        if prop.year_built and prop.year_built < 1960: complexity += 8
        if metrics.cash_flow_before_tax < 0: complexity += 12
        base = average_prior(prior_findings, 60)
        score = max(0, min(100, base - complexity * 0.6))
        positives, concerns = [], []
        if complexity <= 12: positives.append("Deal complexity appears manageable for a small-operator playbook.")
        else: concerns.append("Deal complexity requires experienced property management, contractor control, and lender communication.")
        return self.finding(score=score, confidence=0.50, thesis=f"Sponsor-fit screen estimates complexity at {complexity:.0f} points versus prior committee score {base:.1f}.", positives=positives, concerns=concerns, evidence=[self.assumption("unit_count", prop.unit_count), self.assumption("rehab_budget", prop.rehab_budget)], actions=["Match the business plan to a named operator, property manager, GC, lender, and contingency budget."])
