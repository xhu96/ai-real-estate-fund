from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class PropertyManagementAgent(CommitteeAgent):
    name = "Property Management Agent"
    role = "Assesses management-fee realism, operating complexity, and third-party management needs."
    weight = 0.80
    category = "operations"

    def analyze(self, prop, metrics, data, prior_findings):
        fee_score = score_range(prop.management_rate, 0.13, 0.05, invert=True)
        complexity_penalty = 0 if prop.unit_count <= 2 else 5 if prop.unit_count <= 4 else 12
        score = max(0, fee_score - complexity_penalty)
        positives, concerns = [], []
        if 0.06 <= prop.management_rate <= 0.10: positives.append(f"Management fee of {pct(prop.management_rate)} is in a plausible range.")
        else: concerns.append(f"Management fee of {pct(prop.management_rate)} may be unrealistic for this asset type.")
        if prop.unit_count > 4: concerns.append("Larger asset requires stronger property-management systems than a small rental.")
        return self.finding(score=score, confidence=0.59, thesis=f"Property-management screen reviews {pct(prop.management_rate)} fee and {prop.unit_count} unit operating complexity.", positives=positives, concerns=concerns, evidence=[self.assumption("management_rate", prop.management_rate), self.assumption("unit_count", prop.unit_count)], actions=["Obtain management proposal with leasing fees, renewal fees, maintenance markup, and reporting cadence."])
