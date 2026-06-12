from __future__ import annotations
from .base import CommitteeAgent

class ZoningAndRegulatoryAgent(CommitteeAgent):
    name = "Zoning and Regulatory Agent"
    role = "Flags landlord rules, short-term-rental sensitivity, permitting, and local restriction risk."
    weight = 0.85
    category = "legal"

    def analyze(self, prop, metrics, data, prior_findings):
        landlord_score = data.market_snapshot.landlord_friendliness_score
        score = landlord_score * 10
        concerns, positives = [], []
        if landlord_score >= 7:
            positives.append("Market fixture indicates relatively landlord-friendly rules.")
        elif landlord_score <= 5:
            concerns.append("Market fixture indicates less landlord-friendly rules; eviction and rent-control review are required.")
        if "short" in prop.notes.lower() or "airbnb" in prop.notes.lower():
            concerns.append("Notes imply possible short-term rental use; verify STR registration and zoning constraints.")
            score -= 12
        if prop.property_type.lower() in {"adu", "mixed_use"}:
            concerns.append("Non-standard property type requires zoning and permitted-use confirmation.")
            score -= 8
        return self.finding(
            score=score,
            confidence=0.48,
            thesis=f"Regulatory screen uses landlord-friendliness score of {landlord_score:.1f}/10 plus property-use flags.",
            positives=positives,
            concerns=concerns,
            evidence=[self.market_evidence("landlord_friendliness_score", landlord_score), self.assumption("property_type", prop.property_type), self.assumption("notes", prop.notes[:140])],
            actions=["Verify zoning, rental registration, code violations, permits, and local landlord-tenant rules with professionals."],
        )
