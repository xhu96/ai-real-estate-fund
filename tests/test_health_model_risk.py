from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.production.health import run_health_checks
from ai_real_estate_fund.production.model_risk import evaluate_decision_payload
from ai_real_estate_fund.production.settings import ProductionSettings


class HealthModelRiskTest(unittest.TestCase):
    def test_health_checks_sqlite_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            settings = ProductionSettings(
                database_url=f"sqlite:///{Path(temp) / 'app.db'}",
                audit_database_url=f"sqlite:///{Path(temp) / 'audit.db'}",
                artifact_root=Path(temp) / "reports",
                data_root=Path(temp) / "data",
            )
            report = run_health_checks(settings)
        self.assertEqual(report.status, "ok")
        self.assertEqual(len(report.checks), 4)

    def test_model_risk_on_institutional_payload(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        decision = run_institutional_committee(prop)
        payload = decision.to_dict()
        payload["requires_human_approval"] = True
        report = evaluate_decision_payload(payload)
        self.assertTrue(report.passed, report.to_dict())


if __name__ == "__main__":
    unittest.main()
