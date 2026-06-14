from __future__ import annotations
import unittest
from ai_real_estate_fund.tools import Watchlist, screen_property_payload
from ai_real_estate_fund.tools.geo import haversine_miles

class ToolsV4Tests(unittest.TestCase):
    def test_screening_warns(self):
        self.assertTrue(screen_property_payload({"purchase_price": 0, "market": ""}))

    def test_watchlist(self):
        watchlist = Watchlist()
        watchlist.add("A", "M", "reason", 100)
        self.assertEqual(len(watchlist.to_dict()), 1)

    def test_haversine(self):
        self.assertAlmostEqual(haversine_miles(0, 0, 0, 0), 0)

if __name__ == "__main__":
    unittest.main()
