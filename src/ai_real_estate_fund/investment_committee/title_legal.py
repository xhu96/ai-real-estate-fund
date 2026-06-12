from __future__ import annotations
from .base import CommitteeAgent

class TitleAndLegalAgent(CommitteeAgent):
    name = "Title and Legal Agent"
    role = "Reviews title, entity, contract, easement, lien, and closing-process risk at a high level."
    weight = 0.75
    category = "legal"

    def analyze(self, prop, metrics, data, prior_findings):
        score = 72.0
        concerns, positives = [], ["No title defect is modeled in the structured input."]
        if not prop.address.strip():
            score -= 20
            concerns.append("Missing address prevents parcel, title, tax, and insurance verification.")
        if prop.listing_url == "" and prop.source == "manual":
            score -= 5
            concerns.append("Manual source without listing URL reduces auditability.")
        return self.finding(score=score, confidence=0.40, thesis="Legal/title screen is limited until title commitment, purchase contract, survey, and municipal records are reviewed.", positives=positives, concerns=concerns, evidence=[self.assumption("address", prop.address), self.assumption("source", prop.source), self.assumption("listing_url", prop.listing_url)], actions=["Have counsel review title commitment, survey, entity docs, purchase contract, leases, permits, and municipal compliance."])
