from __future__ import annotations

import unittest

from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.data_sources import LocalDataProvider
from ai_real_estate_fund.finance import underwrite_property
from ai_real_estate_fund.institutional.proforma import build_operating_plan, cumulative_cash_flow, minimum_dscr
from ai_real_estate_fund.institutional.underwriting import RentRollModel
from ai_real_estate_fund.institutional.underwriting import TaxReassessmentModel
from ai_real_estate_fund.institutional.research import AffordabilitySignal
from ai_real_estate_fund.institutional.research import LiquiditySignal


class UnderwritingResearchV5Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.prop = load_property("examples/duplex_sunbelt.json")
        self.metrics = underwrite_property(self.prop)
        self.data = LocalDataProvider().build_bundle(self.prop)

    def test_operating_plan_metrics(self) -> None:
        plan = build_operating_plan(self.prop, self.metrics)
        self.assertEqual(len(plan), self.prop.holding_period_years)
        self.assertGreater(minimum_dscr(plan), 0)
        self.assertNotEqual(cumulative_cash_flow(plan), 0)

    def test_detail_models_return_scores(self) -> None:
        for model in [RentRollModel(), TaxReassessmentModel()]:
            result = model.evaluate(self.prop, self.metrics)
            self.assertGreaterEqual(result.score, 0)
            self.assertLessEqual(result.score, 100)
            self.assertTrue(result.notes)

    def test_research_signals_return_scores(self) -> None:
        for signal in [AffordabilitySignal(), LiquiditySignal()]:
            obs = signal.evaluate(self.prop, self.metrics, self.data)
            self.assertGreaterEqual(obs.normalized_score, 0)
            self.assertLessEqual(obs.normalized_score, 100)
            self.assertTrue(obs.drivers)


if __name__ == "__main__":
    unittest.main()

