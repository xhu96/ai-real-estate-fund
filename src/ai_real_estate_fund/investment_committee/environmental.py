from __future__ import annotations
from .base import CommitteeAgent

class EnvironmentalAgent(CommitteeAgent):
    name = "Environmental Agent"
    role = "Screens for flood, environmental, lead, asbestos, underground tank, and climate-related red flags."
    weight = 0.70
    category = "legal"

    def analyze(self, prop, metrics, data, prior_findings):
        score = 70.0
        concerns, positives = [], []
        notes = prop.notes.lower()
        if any(token in notes for token in ["flood", "mold", "asbestos", "lead", "tank", "environmental"]):
            score -= 25
            concerns.append("Notes contain environmental or hazardous-material keywords.")
        if prop.year_built and prop.year_built < 1978:
            score -= 8
            concerns.append("Pre-1978 property may require lead-based paint disclosure and risk review.")
        if not concerns:
            positives.append("No environmental keywords were found in the provided notes.")
        return self.finding(score=score, confidence=0.42, thesis="Environmental screen is a keyword and age-based preliminary check only.", positives=positives, concerns=concerns, evidence=[self.assumption("year_built", prop.year_built), self.assumption("notes", prop.notes[:160])], actions=["Order appropriate environmental, flood, and hazardous-material diligence for the asset type and location."])
