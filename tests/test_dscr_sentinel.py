"""Characterization test for the no-debt (all-cash) DSCR sentinel.

A zero-leverage deal has infinitely strong debt coverage, represented as
``metrics.dscr == float("inf")``. The scoring path must treat that as the
TOP of the DSCR band (not as a mediocre finite sentinel like 2.0x), and the
JSON-facing serialization must never leak a non-finite float.
"""
from __future__ import annotations

import math
import unittest
from dataclasses import replace

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.data_sources import LocalDataProvider
from ai_real_estate_fund.finance import underwrite_property
from ai_real_estate_fund.institutional.agents.base import WorkstreamAgent
from ai_real_estate_fund.investment_committee import run_property_committee


def _find_non_finite_floats(value: object, path: str = "root") -> list[str]:
    """Recursively collect paths to any float that is inf or nan."""
    bad: list[str] = []
    if isinstance(value, bool):
        return bad
    if isinstance(value, float):
        if not math.isfinite(value):
            bad.append(f"{path}={value!r}")
    elif isinstance(value, dict):
        for key, item in value.items():
            bad.extend(_find_non_finite_floats(item, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            bad.extend(_find_non_finite_floats(item, f"{path}[{index}]"))
    return bad


class NoDebtDscrSentinelTests(unittest.TestCase):
    def setUp(self) -> None:
        base = load_property("examples/duplex_sunbelt.json")
        # All-cash deal: no loan, so no debt service and an infinite DSCR.
        self.no_debt = replace(base, loan_amount=0, annual_interest_rate=0.0)
        # A leveraged comparator with a strong-but-finite DSCR near 1.65x.
        self.strong_finite = self._build_dscr_comparator(base, low=1.55, high=1.75)

    @staticmethod
    def _build_dscr_comparator(base, *, low: float, high: float):
        for loan in range(10_000, int(base.purchase_price), 2_500):
            candidate = replace(base, loan_amount=loan)
            metrics = underwrite_property(candidate)
            if low <= metrics.dscr <= high:
                return candidate
        raise AssertionError("could not construct a finite DSCR comparator near 1.65x")

    def test_no_debt_metrics_dscr_is_infinite(self) -> None:
        metrics = underwrite_property(self.no_debt)
        self.assertEqual(metrics.dscr, float("inf"))
        self.assertEqual(metrics.annual_debt_service, 0.0)

    def test_comparator_has_strong_finite_dscr(self) -> None:
        metrics = underwrite_property(self.strong_finite)
        self.assertTrue(math.isfinite(metrics.dscr))
        self.assertGreaterEqual(metrics.dscr, 1.55)

    def test_screening_committee_serializes_without_non_finite(self) -> None:
        decision = run_property_committee(self.no_debt)
        # Sanity: underwriting kept the infinite DSCR on the in-memory metrics.
        self.assertEqual(decision.metrics.dscr, float("inf"))
        payload = decision.to_dict()
        leaks = _find_non_finite_floats(payload)
        self.assertEqual(leaks, [], f"non-finite floats leaked into screening JSON: {leaks}")

    def test_institutional_committee_serializes_without_non_finite(self) -> None:
        decision = run_institutional_committee(self.no_debt)
        self.assertEqual(decision.metrics.dscr, float("inf"))
        payload = decision.to_dict()
        leaks = _find_non_finite_floats(payload)
        self.assertEqual(leaks, [], f"non-finite floats leaked into institutional JSON: {leaks}")

    def test_serialized_dscr_field_normalizes_to_none(self) -> None:
        # The infinite DSCR specifically becomes None (per models.normalize_for_json),
        # never the string "inf" or a non-finite float.
        payload = run_property_committee(self.no_debt).to_dict()
        self.assertIsNone(payload["metrics"]["dscr"])

    def test_no_debt_dscr_component_is_band_top(self) -> None:
        # The institutional core-metric DSCR component must clamp to the band top (100)
        # for an infinite DSCR, and must be strictly stronger than a real ~1.65x deal.
        provider = LocalDataProvider()
        probe = WorkstreamAgent(name="dscr probe", focus_components=["dscr"])

        no_debt_metrics = underwrite_property(self.no_debt)
        no_debt_components = probe.core_metric_components(
            self.no_debt, no_debt_metrics, provider.build_bundle(self.no_debt)
        )
        finite_metrics = underwrite_property(self.strong_finite)
        finite_components = probe.core_metric_components(
            self.strong_finite, finite_metrics, provider.build_bundle(self.strong_finite)
        )

        self.assertEqual(no_debt_components["dscr"], 100.0)
        # Proves inf is treated as strong, not folded down to a finite sentinel that
        # would tie (or undercut) a merely-good leveraged deal.
        self.assertGreater(no_debt_components["dscr"], finite_components["dscr"])

    def test_screening_dscr_agents_score_no_debt_at_top_of_band(self) -> None:
        # The hand-written screening agents whose DSCR component was previously gated
        # to the 2.0 sentinel must score the no-debt deal at the very top of that
        # component's band. We compare against a leveraged deal: the no-debt deal's
        # DSCR component cannot score worse than the strong-finite comparator's.
        from ai_real_estate_fund.investment_committee.base import score_range

        no_debt_metrics = underwrite_property(self.no_debt)
        finite_metrics = underwrite_property(self.strong_finite)
        for low, high in [(0.95, 1.75), (1.00, 1.65), (0.85, 1.35)]:
            no_debt_score = score_range(no_debt_metrics.dscr, low, high)
            finite_score = score_range(finite_metrics.dscr, low, high)
            self.assertEqual(no_debt_score, 100.0)
            self.assertGreaterEqual(no_debt_score, finite_score)

    def test_unification_has_teeth_on_a_band_whose_top_exceeds_two(self) -> None:
        # Regression guard for the sentinel removal itself. At every band actually used
        # in production today (tops 1.75 / 1.65 / 1.35, and score_threshold 1.25+0.30),
        # the old magic `2.0` already clamped to the band top, so inf and 2.0 score the
        # SAME -- the user-visible effect of this change is currently nil. Its value is
        # removing the magic number and being robust if a band ever tops out above 2.0.
        # This test makes that robustness explicit: on a (1.0, 3.0) band the removed
        # `2.0` sentinel WOULD have undercut a no-debt deal, while inf clamps to the top.
        from ai_real_estate_fund.investment_committee.base import score_range

        inf_score = score_range(float("inf"), 1.0, 3.0)
        old_sentinel_score = score_range(2.0, 1.0, 3.0)
        self.assertEqual(inf_score, 100.0)
        self.assertLess(old_sentinel_score, 100.0)
        self.assertGreater(inf_score, old_sentinel_score)


if __name__ == "__main__":
    unittest.main()
