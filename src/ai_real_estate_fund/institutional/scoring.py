from __future__ import annotations

from statistics import mean, median, pstdev
from typing import Iterable

from ..finance import clamp
from ..models import AgentFinding, Recommendation
from ..scenarios import recommendation_from_score
from .models import GateSeverity, PolicyResult, ScoreFactor, Scorecard


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default


def bounded(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return clamp(value, low, high)


def score_range(value: float, low: float, high: float, *, invert: bool = False) -> float:
    if high == low:
        return 50.0
    raw = (value - low) / (high - low) * 100.0
    if invert:
        raw = 100.0 - raw
    return round(bounded(raw), 1)


def score_threshold(value: float, target: float, *, tolerance: float = 0.15, higher_is_better: bool = True) -> float:
    if target == 0:
        return 50.0
    relative_gap = (value - target) / abs(target)
    if not higher_is_better:
        relative_gap *= -1
    return round(bounded(50.0 + relative_gap / max(tolerance, 0.001) * 25.0), 1)


def weighted_average_scores(items: Iterable[tuple[float, float]]) -> float:
    pairs = [(score, max(weight, 0.0)) for score, weight in items]
    total = sum(weight for _, weight in pairs)
    if total <= 0:
        return 0.0
    return round(sum(score * weight for score, weight in pairs) / total, 1)


def weighted_agent_score(findings: Iterable[AgentFinding]) -> float:
    return weighted_average_scores((finding.score, finding.weight) for finding in findings)


def recommendation_with_policy(score: float, policy_results: list[PolicyResult]) -> Recommendation:
    hard_stop_failed = any(not result.passed and result.severity == GateSeverity.HARD_STOP for result in policy_results)
    if hard_stop_failed:
        return Recommendation.PASS
    warning_count = sum(1 for result in policy_results if not result.passed and result.severity == GateSeverity.WARNING)
    adjusted = score - min(12.0, warning_count * 2.5)
    return recommendation_from_score(adjusted)


def confidence_from_evidence(evidence_count: int, data_quality: float, prior_count: int = 0) -> float:
    evidence_component = min(0.20, evidence_count * 0.015)
    quality_component = max(0.0, min(0.25, (data_quality - 50.0) / 200.0))
    prior_component = min(0.10, prior_count * 0.005)
    return round(max(0.35, min(0.95, 0.45 + evidence_component + quality_component + prior_component)), 2)


def score_dispersion(findings: list[AgentFinding]) -> float:
    if len(findings) < 2:
        return 0.0
    return round(pstdev([finding.score for finding in findings]), 2)


def dissent_level(findings: list[AgentFinding]) -> str:
    dispersion = score_dispersion(findings)
    if dispersion >= 22:
        return "high"
    if dispersion >= 12:
        return "medium"
    return "low"


def top_findings(findings: list[AgentFinding], n: int = 5) -> list[AgentFinding]:
    return sorted(findings, key=lambda item: item.score, reverse=True)[:n]


def weakest_findings(findings: list[AgentFinding], n: int = 5) -> list[AgentFinding]:
    return sorted(findings, key=lambda item: item.score)[:n]


def scorecard_from_agent_group(name: str, category: str, findings: list[AgentFinding]) -> Scorecard:
    factors = [
        ScoreFactor(
            name=finding.agent_name,
            value=finding.score,
            score=finding.score,
            weight=finding.weight,
            explanation=finding.thesis,
            source=finding.model,
        )
        for finding in findings
    ]
    confidence = mean([f.confidence for f in findings]) if findings else 0.50
    return Scorecard(name=name, category=category, factors=factors, confidence=round(confidence, 2))


def percentile_rank(value: float, sample: Iterable[float]) -> float:
    values = sorted(float(item) for item in sample)
    if not values:
        return 50.0
    less = sum(1 for item in values if item < value)
    equal = sum(1 for item in values if item == value)
    return round((less + equal * 0.5) / len(values) * 100.0, 1)


def robust_z_score(value: float, sample: Iterable[float]) -> float:
    values = sorted(float(item) for item in sample)
    if not values:
        return 0.0
    med = median(values)
    deviations = [abs(item - med) for item in values]
    mad = median(deviations) or 1.0
    return round((value - med) / (1.4826 * mad), 3)

