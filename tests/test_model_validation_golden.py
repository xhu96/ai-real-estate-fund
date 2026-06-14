"""Golden regression test for the consolidated model_validation family.

Proves that the single-base-class refactor is byte-identical to the original
20-clone behaviour, and that every original class name is still importable
from the package level and constructs the right configured instance.
"""

from __future__ import annotations

import json
import unittest
from dataclasses import asdict, is_dataclass
from importlib import import_module
from pathlib import Path

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property

GOLDEN_PATH = Path(__file__).parent / "data" / "golden_model_validation.json"
PACKAGE = "ai_real_estate_fund.institutional.model_validation"


def _canonical_output(cls_name: str) -> object:
    module = import_module(PACKAGE)
    cls = getattr(module, cls_name)
    out = cls().validate(_DECISION)
    if is_dataclass(out):
        out = asdict(out)
    return out


# Build the canonical decision fixture once (deterministic; no LLM client).
_PROP = load_property("examples/duplex_sunbelt.json")
_DECISION = run_institutional_committee(_PROP)
_GOLDEN: dict[str, object] = json.loads(GOLDEN_PATH.read_text())


class ModelValidationGoldenTests(unittest.TestCase):
    def test_class_name_set_matches_snapshot(self) -> None:
        module = import_module(PACKAGE)
        recomputed = {
            name for name in dir(module)
            if name.endswith("Validator") and name != "BaseValidator"
        }
        self.assertEqual(recomputed, set(_GOLDEN), "validator class names drifted")

    def test_each_class_is_byte_identical(self) -> None:
        for cls_name, expected in _GOLDEN.items():
            with self.subTest(validator=cls_name):
                module = import_module(PACKAGE)
                self.assertTrue(
                    hasattr(module, cls_name),
                    f"{cls_name} not importable from package level",
                )
                actual = _canonical_output(cls_name)
                self.assertEqual(
                    actual, expected, f"{cls_name} output diverged from golden master"
                )

    def test_result_class_names_preserved(self) -> None:
        module = import_module(PACKAGE)
        for cls_name in _GOLDEN:
            result_name = cls_name + "Result"
            with self.subTest(result=result_name):
                self.assertTrue(
                    hasattr(module, result_name),
                    f"{result_name} not importable from package level",
                )


if __name__ == "__main__":
    unittest.main()
