"""Golden regression test for the consolidated underwriting model family.

Proves byte-identical behavior plus class-name preservation after the 25
``*_model.py`` clones were collapsed into one base ``Model`` + a registry.

For every class name in the frozen snapshot we:
  * import it from the package level (name preservation), and
  * recompute the canonical output ``Model().evaluate(prop, metrics).to_dict()``
    and assert it equals the snapshot value exactly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_real_estate_fund import institutional
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.finance import underwrite_property
from ai_real_estate_fund.institutional import underwriting

GOLDEN_PATH = Path(__file__).parent / "data" / "golden_underwriting.json"


def _load_snapshot() -> dict[str, dict]:
    return json.loads(GOLDEN_PATH.read_text())


SNAPSHOT = _load_snapshot()


@pytest.fixture(scope="module")
def fixtures():
    prop = load_property("examples/duplex_sunbelt.json")
    metrics = underwrite_property(prop)
    return prop, metrics


def test_class_name_set_matches_snapshot():
    """The package must expose exactly the snapshot's class names."""
    exposed = {
        name
        for name in dir(underwriting)
        if name.endswith("Model") and name != "Model"
    }
    assert exposed == set(SNAPSHOT), (
        f"missing={set(SNAPSHOT) - exposed}, extra={exposed - set(SNAPSHOT)}"
    )


@pytest.mark.parametrize("class_name", sorted(SNAPSHOT))
def test_canonical_output_byte_identical(class_name, fixtures):
    prop, metrics = fixtures
    cls = getattr(underwriting, class_name)
    # Name preservation: the exposed class reports its original name.
    assert cls.__name__ == class_name
    actual = cls().evaluate(prop, metrics).to_dict()
    # Round-trip through JSON so the comparison matches the frozen snapshot
    # representation exactly (same as how it was serialized).
    actual = json.loads(json.dumps(actual))
    assert actual == SNAPSHOT[class_name]


def test_package_level_import_constructs_configured_instance():
    """`from ...underwriting import <ClassName>` builds the right instance."""
    for class_name in SNAPSHOT:
        assert hasattr(underwriting, class_name)
    # Spot-check the special equity-waterfall subject is preserved verbatim.
    assert underwriting.WaterfallModel().subject == "equity waterfall"
    # institutional namespace should still re-expose the underwriting package.
    assert institutional.underwriting is underwriting
