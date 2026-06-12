from __future__ import annotations
import unittest
from ai_real_estate_fund.backtesting.engine import BacktestEngine
from ai_real_estate_fund.backtesting.fixtures import example_historical_deals

class BacktestingV3Tests(unittest.TestCase):
    def test_fixture_backtest_runs(self):
        result = BacktestEngine().run(example_historical_deals("examples/properties.csv"))
        self.assertEqual(len(result.trades), 3)
        self.assertGreaterEqual(result.ending_equity, 0)

if __name__ == "__main__":
    unittest.main()
