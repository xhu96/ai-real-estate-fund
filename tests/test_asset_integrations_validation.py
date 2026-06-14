from __future__ import annotations

import unittest

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.finance import underwrite_property
from ai_real_estate_fund.institutional.asset_management import OccupancyMonitor
from ai_real_estate_fund.institutional.integrations import CountyAssessorAdapter, CountyAssessorAdapterQuery
from ai_real_estate_fund.institutional.model_validation import HardStopEnforcementValidator


class AssetIntegrationsValidationV5Tests(unittest.TestCase):
    def test_asset_monitor_report(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        metrics = underwrite_property(prop)
        report = OccupancyMonitor().report(prop, metrics)
        self.assertEqual(report.asset_name, prop.name)
        self.assertGreaterEqual(report.health_score(), 0)
        self.assertTrue(report.kpis)

    def test_integration_adapter_fixture(self) -> None:
        adapter = CountyAssessorAdapter()
        records = adapter.fetch(CountyAssessorAdapterQuery(address="123 Test Ave", market="San Antonio, TX"))
        self.assertEqual(len(records), 3)
        normalized = adapter.normalize(records)
        self.assertIn("fields", normalized[0])

    def test_model_validation_result(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        decision = run_institutional_committee(prop)
        result = HardStopEnforcementValidator().validate(decision)
        self.assertGreaterEqual(result.score, 0)
        self.assertTrue(result.findings)


if __name__ == "__main__":
    unittest.main()

