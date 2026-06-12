from __future__ import annotations
import unittest
from ai_real_estate_fund.validation import calibration_table, population_stability_index

class ValidationV4Tests(unittest.TestCase):
    def test_calibration_table(self):
        rows = calibration_table([10, 30, 70, 90], [False, False, True, True], buckets=2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["success_rate"], 1.0)

    def test_psi_non_negative(self):
        self.assertGreaterEqual(population_stability_index([1,2,3], [1,2,4]), 0)

if __name__ == "__main__":
    unittest.main()
