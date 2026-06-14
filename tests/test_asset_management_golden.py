"""Golden-master regression test for the asset_management monitor family.

Proves byte-identical behavior and class-name preservation after the clone
family was consolidated into base.py + specs.py. Loads the frozen snapshot,
asserts the set of class names matches exactly, and for every name recomputes
the canonical report and asserts it equals the snapshot value exactly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import ai_real_estate_fund.institutional.asset_management as asset_management
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.finance import underwrite_property

GOLDEN_PATH = Path(__file__).parent / "data" / "golden_asset_management.json"


@pytest.fixture(scope="module")
def golden() -> dict[str, dict]:
    return json.loads(GOLDEN_PATH.read_text())


@pytest.fixture(scope="module")
def fixtures():
    prop = load_property("examples/duplex_sunbelt.json")
    metrics = underwrite_property(prop)
    return prop, metrics


def test_class_names_match_snapshot(golden: dict[str, dict]) -> None:
    """No missing or extra class names versus the frozen snapshot."""
    registry_names = set(asset_management.REGISTRY.keys())
    assert registry_names == set(golden.keys())


def test_each_class_byte_identical(golden: dict[str, dict], fixtures) -> None:
    """Each preserved class, imported from the package, reproduces the
    snapshot output exactly (byte-identical)."""
    prop, metrics = fixtures
    for class_name, expected in sorted(golden.items()):
        cls = getattr(asset_management, class_name)
        assert cls.__name__ == class_name
        actual = cls().report(prop, metrics).to_dict()
        assert actual == expected, f"{class_name} output diverged from snapshot"
