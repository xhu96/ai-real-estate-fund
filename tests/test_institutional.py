from __future__ import annotations

import unittest

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.institutional.data_room import build_data_room_manifest
from ai_real_estate_fund.institutional.policy import evaluate_policy
from ai_real_estate_fund.finance import underwrite_property
from ai_real_estate_fund.data_sources import LocalDataProvider
from ai_real_estate_fund.models import Recommendation


class InstitutionalCommitteeTests(unittest.TestCase):
    def test_specs_carry_methodology_sources(self) -> None:
        from ai_real_estate_fund.institutional.agents import AGENT_SPECS

        cited = [spec for spec in AGENT_SPECS if spec.sources]
        self.assertGreaterEqual(len(cited), 50)
        debt = next(spec for spec in AGENT_SPECS if spec.name == "Debt Yield Agent")
        self.assertTrue(any("Form 4660" in source for source in debt.sources))

    def test_memo_lists_methodology_sources(self) -> None:
        from ai_real_estate_fund.committee import run_institutional_committee
        from ai_real_estate_fund.data_loader import load_property
        from ai_real_estate_fund.institutional.memo import render_institutional_memo

        memo = render_institutional_memo(run_institutional_committee(load_property("examples/duplex_sunbelt.json")))
        self.assertIn("## Methodology Sources", memo)
        self.assertIn("Form 4660", memo)

    def test_runs_large_committee(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        decision = run_institutional_committee(prop)
        self.assertGreaterEqual(len(decision.findings), 70)
        self.assertGreater(decision.overall_score, 0)
        self.assertIn(decision.recommendation, set(Recommendation))
        self.assertGreaterEqual(len(decision.scorecards), 6)
        self.assertTrue(decision.operating_plan)

    def test_to_dict_is_json_safe(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        decision = run_institutional_committee(prop)
        payload = decision.to_dict()
        self.assertIsInstance(payload["recommendation"], str)
        self.assertIsInstance(payload["findings"], list)
        self.assertIn("hard_stops", payload)

    def test_policy_and_data_room_helpers(self) -> None:
        prop = load_property("examples/duplex_sunbelt.json")
        metrics = underwrite_property(prop)
        data = LocalDataProvider().build_bundle(prop)
        manifest = build_data_room_manifest(prop, data)
        self.assertGreater(len(manifest.documents), 20)
        results = evaluate_policy(run_institutional_committee(prop).policy, prop, metrics, data, 70)
        self.assertGreaterEqual(len(results), 8)


if __name__ == "__main__":
    unittest.main()

