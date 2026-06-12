from __future__ import annotations
from .base import CommitteeAgent

class NeighborhoodQualityAgent(CommitteeAgent):
    name = "Neighborhood Quality Agent"
    role = "Scores block-level quality proxies: neighborhood, school, crime, liquidity, and tenant depth."
    weight = 0.95
    category = "market"

    def analyze(self, prop, metrics, data, prior_findings):
        crime_component = 10 - max(1, min(10, prop.crime_risk_score))
        score = (prop.neighborhood_score * 0.35 + prop.school_score * 0.25 + crime_component * 0.25 + prop.liquidity_score * 0.15) * 10
        positives, concerns = [], []
        if prop.neighborhood_score >= 7: positives.append("Neighborhood score supports tenant demand and exit liquidity.")
        else: concerns.append("Neighborhood score is not strong enough to rely on broad market averages.")
        if prop.crime_risk_score >= 7: concerns.append("Crime-risk score requires street-by-street validation.")
        if prop.school_score >= 7: positives.append("School score is a positive demand signal for family rentals.")
        return self.finding(score=score, confidence=0.58, thesis=f"Neighborhood quality combines subject scores: neighborhood {prop.neighborhood_score:.1f}, school {prop.school_score:.1f}, crime risk {prop.crime_risk_score:.1f}, liquidity {prop.liquidity_score:.1f}.", positives=positives, concerns=concerns, evidence=[self.assumption("neighborhood_score", prop.neighborhood_score), self.assumption("school_score", prop.school_score), self.assumption("crime_risk_score", prop.crime_risk_score)], actions=["Verify the exact block, not just ZIP-code averages, with local operators and municipal data."])
