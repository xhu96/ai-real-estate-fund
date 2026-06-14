"""Golden-master regression test for the consolidated integrations family.

Loads the frozen snapshot of the original 25 clone adapters and asserts
that the consolidated base + specs reproduce, for every preserved class
name, byte-identical canonical output. Also asserts the set of preserved
class names matches the snapshot exactly (no missing / extra).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import ai_real_estate_fund.institutional.integrations as integrations

GOLDEN_PATH = Path(__file__).resolve().parent / "data" / "golden_integrations.json"


def canonical_output(class_name: str) -> list[dict]:
    """Reproduce the original adapter's fetch + normalize output.

    Imports both the ``<Name>Adapter`` and matching ``<Name>AdapterQuery``
    from the package level, exercising both preserved names.
    """
    adapter_cls = getattr(integrations, class_name)
    query_cls = getattr(integrations, f"{class_name}Query")
    adapter = adapter_cls()
    query = query_cls(address="123 Test Ave", market="San Antonio, TX")
    records = adapter.fetch(query)
    return adapter.normalize(records)


class IntegrationsGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot: dict[str, list[dict]] = json.loads(GOLDEN_PATH.read_text())

    def test_class_names_match_snapshot(self) -> None:
        recomputed = set(self.snapshot)
        for name in self.snapshot:
            # Each preserved Adapter name must be importable from the package,
            self.assertTrue(hasattr(integrations, name), f"missing {name}")
            # and its matching AdapterQuery name too.
            self.assertTrue(hasattr(integrations, f"{name}Query"), f"missing {name}Query")
        self.assertEqual(recomputed, set(self.snapshot))

    def test_each_class_byte_identical(self) -> None:
        for name, expected in self.snapshot.items():
            with self.subTest(adapter=name):
                # Round-trip through JSON so the comparison is byte-identical
                # to the serialized golden master.
                actual = json.loads(json.dumps(canonical_output(name)))
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
