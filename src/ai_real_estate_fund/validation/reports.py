from __future__ import annotations
from .schemas import ValidationFinding

def render_validation_report(findings: list[ValidationFinding]) -> str:
    lines = ["# Validation Report", "", "| Check | Status | Metric | Message |", "|---|---|---:|---|"]
    for finding in findings:
        lines.append(f"| {finding.name} | {finding.status} | {finding.metric:.3f} | {finding.message} |")
    return "\n".join(lines) + "\n"
