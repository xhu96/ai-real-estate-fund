from __future__ import annotations

import unittest

from ai_real_estate_fund.institutional.scoring import recommendation_from_score as institutional_rec
from ai_real_estate_fund.models import Recommendation
from ai_real_estate_fund.scenarios import (
    BUY_THRESHOLD,
    NEGOTIATE_THRESHOLD,
    WATCHLIST_THRESHOLD,
    recommendation_from_score as screening_rec,
)


class RecommendationThresholdTest(unittest.TestCase):
    def test_single_source_of_truth(self) -> None:
        # Both committees must resolve verdicts through the SAME function, so the
        # same score can never yield a different recommendation by engine.
        self.assertIs(institutional_rec, screening_rec)

    def test_unified_thresholds(self) -> None:
        self.assertEqual((BUY_THRESHOLD, NEGOTIATE_THRESHOLD, WATCHLIST_THRESHOLD), (78.0, 66.0, 52.0))
        cases = {
            90.0: Recommendation.BUY,
            78.0: Recommendation.BUY,
            77.9: Recommendation.NEGOTIATE,
            67.0: Recommendation.NEGOTIATE,  # was WATCHLIST under the old screening 68 cutoff
            66.0: Recommendation.NEGOTIATE,
            65.9: Recommendation.WATCHLIST,
            53.0: Recommendation.WATCHLIST,  # was PASS under the old screening 55 cutoff
            52.0: Recommendation.WATCHLIST,
            51.9: Recommendation.PASS,
            0.0: Recommendation.PASS,
        }
        for score, expected in cases.items():
            self.assertEqual(screening_rec(score), expected, f"score {score}")


if __name__ == "__main__":
    unittest.main()
