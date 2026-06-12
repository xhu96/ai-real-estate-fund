from __future__ import annotations
import unittest
from ai_real_estate_fund.valuation import discounted_cash_flow_value, implied_value_from_noi, yield_on_cost

class ValuationV3Tests(unittest.TestCase):
    def test_cap_rate_value(self):
        self.assertEqual(implied_value_from_noi(75_000, 0.075), 1_000_000)

    def test_dcf_positive(self):
        self.assertGreater(discounted_cash_flow_value(50_000, 0.03, 0.07, 0.10, 5), 0)

    def test_yield_on_cost(self):
        self.assertAlmostEqual(yield_on_cost(80_000, 1_000_000), 0.08)

if __name__ == "__main__":
    unittest.main()
