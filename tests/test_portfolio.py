from __future__ import annotations
import unittest
from ai_real_estate_fund.portfolio import AllocationCandidate, GreedyPortfolioOptimizer, PortfolioConstraints

class PortfolioV3Tests(unittest.TestCase):
    def test_optimizer_selects_eligible_candidate(self):
        candidates = [AllocationCandidate("A", "San Antonio, TX", 82, 75, 100_000, 0.18, 0.08, 0.075, "BUY")]
        plan = GreedyPortfolioOptimizer().optimize(candidates, PortfolioConstraints(total_equity_budget=1_000_000))
        self.assertEqual(len(plan.selected), 1)

if __name__ == "__main__":
    unittest.main()
