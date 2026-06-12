from __future__ import annotations
import unittest
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.investment_committee import build_default_agents, run_property_committee

class ExtraAgentsV4Tests(unittest.TestCase):
    def test_registry_has_expanded_agent_count(self):
        self.assertGreaterEqual(len(build_default_agents()), 29)

    def test_decision_contains_chair_agent(self):
        decision = run_property_committee(load_property("examples/duplex_sunbelt.json"))
        names = {finding.agent_name for finding in decision.findings}
        self.assertIn("Investment Committee Chair Agent", names)
        self.assertGreaterEqual(len(decision.findings), 29)

if __name__ == "__main__":
    unittest.main()
