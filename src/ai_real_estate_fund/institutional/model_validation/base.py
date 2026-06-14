"""Generic model-validation check shared by every validator in this package.

Every validator in this package is a structurally identical clone that differs
only by its label (the ``name`` constant), its human docstring, and the names of
its public ``*Validator`` / ``*ValidatorResult`` classes. The shared behaviour
lives here once; per-validator constants live in :mod:`.specs`.

Note: this family is an illustrative, uncalibrated deterministic heuristic
that demonstrates the *shape* of a production fund system. Its check
thresholds and validator labels are placeholders, not validated models. It is
standalone and not wired into the committee decision (only sampled by a couple
of tests).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol


class DictLikeDecision(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


@dataclass(slots=True)
class ValidatorResult:
    validator: str
    passed: bool
    score: float
    findings: list[str]
    remediation: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidatorSpec:
    """Per-validator constants extracted verbatim from each original clone."""

    module: str
    class_name: str
    result_class_name: str
    name: str
    description: str


class BaseValidator:
    """Shared validation logic. Method bodies copied verbatim from the clones."""

    name = ""

    def extract(self, decision: DictLikeDecision | dict[str, Any]) -> dict[str, Any]:
        if isinstance(decision, dict):
            return decision
        return decision.to_dict()

    def score(self, payload: dict[str, Any]) -> float:
        score = 100.0
        if not payload.get("findings"):
            score -= 25.0
        if not payload.get("policy_results"):
            score -= 20.0
        if not payload.get("data_room"):
            score -= 15.0
        hard_stops = payload.get("hard_stops") or []
        if hard_stops and payload.get("recommendation") == "BUY":
            score -= 35.0
        if payload.get("overall_score", 0) <= 0:
            score -= 20.0
        if len(payload.get("next_steps") or []) < 3:
            score -= 10.0
        return max(0.0, round(score, 1))

    def findings(self, payload: dict[str, Any]) -> list[str]:
        items: list[str] = []
        if not payload.get("findings"):
            items.append("No agent findings available for validation.")
        if not payload.get("policy_results"):
            items.append("No policy gate results available.")
        if payload.get("hard_stops") and payload.get("recommendation") == "BUY":
            items.append("BUY recommendation conflicts with unresolved hard stops.")
        if not items:
            items.append(f"{self.name} did not identify a blocking validation issue.")
        return items

    def remediation(self, payload: dict[str, Any]) -> list[str]:
        actions: list[str] = []
        if not payload.get("data_room"):
            actions.append("Attach data-room manifest to the decision packet.")
        if not payload.get("policy_results"):
            actions.append("Run investment-policy gates before final IC approval.")
        if payload.get("hard_stops"):
            actions.append("Close or formally override hard stops with documented approval.")
        if not actions:
            actions.append("Archive validation result with the committee packet.")
        return actions

    def validate(self, decision: DictLikeDecision | dict[str, Any]) -> ValidatorResult:
        payload = self.extract(decision)
        score = self.score(payload)
        return ValidatorResult(
            validator=self.name,
            passed=score >= 70.0,
            score=score,
            findings=self.findings(payload),
            remediation=self.remediation(payload),
        )
