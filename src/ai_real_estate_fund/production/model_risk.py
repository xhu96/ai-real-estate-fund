from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ModelControl:
    name: str
    passed: bool
    severity: str
    evidence: str
    remediation: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ModelRiskReport:
    controls: list[ModelControl] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(control.passed or control.severity != "fail" for control in self.controls)

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "controls": [control.to_dict() for control in self.controls]}


def evaluate_decision_payload(payload: dict[str, Any]) -> ModelRiskReport:
    controls: list[ModelControl] = []
    disclaimer = str(payload.get("disclaimer", ""))
    controls.append(ModelControl(
        name="disclaimer_present",
        passed="not financial" in disclaimer.lower() or "educational" in disclaimer.lower(),
        severity="fail",
        evidence="Decision disclaimer checked.",
        remediation="Add a clear educational-use and no-advice disclaimer to every API/CLI response.",
    ))
    controls.append(ModelControl(
        name="hard_stops_reported",
        passed="hard_stops" in payload,
        severity="fail",
        evidence="Policy gate hard-stop field checked.",
        remediation="Expose hard_stops in the decision payload.",
    ))
    controls.append(ModelControl(
        name="human_review_for_buy",
        passed=str(payload.get("recommendation", "")).upper() != "BUY" or bool(payload.get("requires_human_approval", True)),
        severity="warn",
        evidence="BUY recommendation approval gate checked.",
        remediation="Require human approval before any BUY recommendation moves to execution.",
    ))
    score = payload.get("overall_score")
    controls.append(ModelControl(
        name="score_range",
        passed=isinstance(score, (int, float)) and 0 <= float(score) <= 100,
        severity="fail",
        evidence=f"overall_score={score!r}",
        remediation="Normalize all model scores to [0, 100].",
    ))
    findings = payload.get("findings", [])
    controls.append(ModelControl(
        name="agent_findings_present",
        passed=isinstance(findings, list) and len(findings) >= 10,
        severity="fail",
        evidence=f"finding_count={len(findings) if isinstance(findings, list) else 'n/a'}",
        remediation="Return detailed agent findings and evidence for auditability.",
    ))
    return ModelRiskReport(controls)
