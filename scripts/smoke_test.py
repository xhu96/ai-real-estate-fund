#!/usr/bin/env python
from __future__ import annotations

import json
from pathlib import Path

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.production.model_risk import evaluate_decision_payload


def main() -> None:
    path = Path("examples/duplex_sunbelt.json")
    prop = load_property(path)
    decision = run_institutional_committee(prop)
    payload = decision.to_dict()
    report = evaluate_decision_payload(payload)
    summary = {
        "property": prop.name,
        "recommendation": payload["recommendation"],
        "overall_score": payload["overall_score"],
        "findings": len(payload.get("findings", [])),
        "model_risk_passed": report.passed,
    }
    print(json.dumps(summary, indent=2))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
