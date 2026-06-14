from __future__ import annotations

import unittest

from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.sensitivity import run_sensitivity


class SensitivityTests(unittest.TestCase):
    def test_sensitivity_returns_cases(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        cases = run_sensitivity(prop)
        self.assertGreaterEqual(len(cases), 5)
        names = [name for name, _memo in cases]
        self.assertIn("Base case", names)
        self.assertIn("Downside case", names)


if __name__ == "__main__":
    unittest.main()
