from __future__ import annotations
import unittest
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.investment_committee import ScreeningCommittee, build_default_agents, run_property_committee
from ai_real_estate_fund.models import Recommendation

class ScreeningCommitteeTests(unittest.TestCase):
    def test_default_registry_has_many_agents(self):
        self.assertGreaterEqual(len(build_default_agents()), 15)

    def test_committee_returns_decision_with_findings(self):
        prop = load_property("examples/duplex_sunbelt.json")
        decision = run_property_committee(prop)
        self.assertGreaterEqual(len(decision.findings), 15)
        self.assertGreater(decision.overall_score, 0)
        self.assertIn(decision.recommendation, set(Recommendation))

    def test_custom_committee_can_run(self):
        prop = load_property("examples/single_family_midwest.json")
        decision = ScreeningCommittee().run(prop)
        self.assertTrue(decision.risk_register)

if __name__ == "__main__":
    unittest.main()
