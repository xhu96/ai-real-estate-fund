from __future__ import annotations
from .base import CommitteeAgent

class DataQualityAgent(CommitteeAgent):
    name = "Data Quality Agent"
    role = "Scores completeness, confidence, missing fields, and evidence depth."
    weight = 1.00
    category = "data"

    def analyze(self, prop, metrics, data, prior_findings):
        report = data.data_quality
        if report is None:
            return self.finding(score=45, confidence=0.80, thesis="No data-quality report was available.", concerns=["Data-provider bundle did not include quality scoring."], evidence=[], actions=["Attach explicit data-quality scoring to every provider."])
        score = report.completeness_score * 0.70 + report.confidence_score * 0.30
        positives, concerns = [], []
        if report.completeness_score >= 80: positives.append("Input completeness is acceptable for a preliminary committee run.")
        else: concerns.append("Input completeness is below preferred threshold.")
        concerns.extend(report.warnings[:3])
        return self.finding(score=score, confidence=0.88, thesis=f"Data quality score combines completeness {report.completeness_score:.1f} and confidence {report.confidence_score:.1f} across {report.evidence_count} evidence items.", positives=positives, concerns=concerns, evidence=[self.market_evidence("completeness_score", report.completeness_score), self.market_evidence("confidence_score", report.confidence_score), self.market_evidence("evidence_count", report.evidence_count)], actions=["Close missing fields and attach external source IDs before treating the memo as investment-grade."])
