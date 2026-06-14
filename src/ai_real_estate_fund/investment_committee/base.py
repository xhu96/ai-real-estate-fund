from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import mean, median
from typing import Iterable

from ..finance import clamp
from ..models import (
    AgentFinding,
    DiligenceDataBundle,
    EvidenceItem,
    PropertyInput,
    UnderwritingMetrics,
)
from ..scenarios import recommendation_from_score


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


def money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.0f}"


def safe_mean(values: Iterable[float]) -> float:
    values = list(values)
    return mean(values) if values else 0.0


def safe_median(values: Iterable[float]) -> float:
    values = list(values)
    return median(values) if values else 0.0


def score_range(value: float, low: float, high: float, invert: bool = False) -> float:
    """Map a metric into a 0-100 score with optional inversion."""
    if high == low:
        return 50.0
    raw = (value - low) / (high - low) * 100
    if invert:
        raw = 100 - raw
    return clamp(raw)


class CommitteeAgent(ABC):
    name = "Committee Agent"
    role = "Reviews one diligence workstream."
    weight = 1.0
    category = "general"

    @abstractmethod
    def analyze(
        self,
        prop: PropertyInput,
        metrics: UnderwritingMetrics,
        data: DiligenceDataBundle,
        prior_findings: list[AgentFinding],
    ) -> AgentFinding:
        raise NotImplementedError

    def finding(
        self,
        *,
        score: float,
        confidence: float,
        thesis: str,
        positives: list[str] | None = None,
        concerns: list[str] | None = None,
        evidence: list[EvidenceItem] | None = None,
        actions: list[str] | None = None,
    ) -> AgentFinding:
        normalized = round(clamp(score), 1)
        return AgentFinding(
            agent_name=self.name,
            role=self.role,
            score=normalized,
            recommendation=recommendation_from_score(normalized),
            confidence=round(clamp(confidence, 0.0, 1.0), 2),
            thesis=thesis,
            positives=positives or [],
            concerns=concerns or [],
            evidence=evidence or [],
            actions=actions or [],
            weight=self.weight,
        )

    def assumption(self, label: str, value: object, confidence: float = 0.70) -> EvidenceItem:
        return EvidenceItem(
            source="property_input",
            label=label,
            value=value if isinstance(value, (str, int, float, bool)) or value is None else str(value),
            category="assumption",
            confidence=confidence,
        )

    def market_evidence(self, label: str, value: object, confidence: float = 0.72) -> EvidenceItem:
        return EvidenceItem(
            source="market_snapshot",
            label=label,
            value=value if isinstance(value, (str, int, float, bool)) or value is None else str(value),
            category="market",
            confidence=confidence,
        )

    def metric(self, label: str, value: object, confidence: float = 0.78) -> EvidenceItem:
        return EvidenceItem(
            source="underwriting_engine",
            label=label,
            value=value if isinstance(value, (str, int, float, bool)) or value is None else str(value),
            category="metric",
            confidence=confidence,
        )


def prior_score(prior_findings: list[AgentFinding], name: str, default: float = 50.0) -> float:
    for finding in prior_findings:
        if finding.agent_name == name:
            return finding.score
    return default


def average_prior(prior_findings: list[AgentFinding], default: float = 50.0) -> float:
    if not prior_findings:
        return default
    total_weight = sum(max(f.weight, 0.01) for f in prior_findings)
    return sum(f.score * max(f.weight, 0.01) for f in prior_findings) / total_weight
