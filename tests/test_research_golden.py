from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path

from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.data_sources import LocalDataProvider
from ai_real_estate_fund.finance import underwrite_property

GOLDEN_PATH = Path(__file__).parent / "data" / "golden_research.json"


class ResearchGoldenTest(unittest.TestCase):
    """Proves the consolidated research signals are byte-identical to the
    frozen original behavior, and that every original class name is preserved
    and importable at the package level."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.golden = json.loads(GOLDEN_PATH.read_text())
        cls.prop = load_property("examples/duplex_sunbelt.json")
        cls.metrics = underwrite_property(cls.prop)
        cls.data = LocalDataProvider().build_bundle(cls.prop)
        cls.research = importlib.import_module(
            "ai_real_estate_fund.institutional.research"
        )

    def test_class_name_set_matches_snapshot(self) -> None:
        expected = set(self.golden)
        actual = {
            name
            for name in dir(self.research)
            if name.endswith("Signal") and name != "BaseSignal"
        }
        self.assertEqual(
            actual,
            expected,
            msg="research package class names diverged from golden snapshot",
        )

    def test_every_class_is_byte_identical(self) -> None:
        for name, expected_output in self.golden.items():
            with self.subTest(signal=name):
                cls = getattr(self.research, name)
                self.assertEqual(cls.__name__, name)
                inst = cls()
                output = inst.evaluate(self.prop, self.metrics, self.data).to_dict()
                self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
