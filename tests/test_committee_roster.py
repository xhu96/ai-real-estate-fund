from __future__ import annotations

import dataclasses
import unittest

from tests.test_phase1_api import _client


# Canonical category order with expected per-category agent counts.
_EXPECTED = (
    ("acquisition", "Acquisition", 5),
    ("income", "Income", 7),
    ("expenses", "Expenses", 9),
    ("debt", "Debt", 9),
    ("physical", "Physical condition", 11),
    ("market", "Market", 14),
    ("portfolio", "Portfolio & returns", 9),
    ("governance", "Governance", 13),
)


class CommitteeRosterTest(unittest.TestCase):
    def setUp(self) -> None:
        # Force demo-open defaults so require_scope("read") passes without a key.
        from app.backend.settings import settings

        self._saved_production = settings.production
        settings.production = dataclasses.replace(
            settings.production,
            environment="development",
            require_api_key=False,
            enable_demo_mode=True,
        )

    def tearDown(self) -> None:
        from app.backend.settings import settings

        settings.production = self._saved_production

    def test_roster_contract(self) -> None:
        client = _client()
        response = client.get("/committee/roster")
        self.assertEqual(response.status_code, 200, response.text)

        body = response.json()
        self.assertEqual(body["total"], 77)

        categories = body["categories"]
        # All 8 keys present, in canonical order.
        self.assertEqual(
            [cat["key"] for cat in categories],
            [key for key, _label, _count in _EXPECTED],
        )
        # Labels match the canonical mapping.
        self.assertEqual(
            [cat["label"] for cat in categories],
            [label for _key, label, _count in _EXPECTED],
        )
        # Per-category counts match.
        self.assertEqual(
            [cat["count"] for cat in categories],
            [count for _key, _label, count in _EXPECTED],
        )
        # Each declared count matches the number of serialized agents.
        for cat in categories:
            self.assertEqual(cat["count"], len(cat["agents"]), cat["key"])
        # Sum of counts equals the total.
        self.assertEqual(sum(cat["count"] for cat in categories), 77)

    def test_sample_agent_shape(self) -> None:
        client = _client()
        body = client.get("/committee/roster").json()

        acquisition = next(c for c in body["categories"] if c["key"] == "acquisition")
        agent = acquisition["agents"][0]
        self.assertEqual(
            set(agent.keys()),
            {"name", "weight", "role", "focus_components", "positive", "concern", "action", "sources"},
        )
        self.assertEqual(agent["name"], "Acquisition Pricing Agent")
        self.assertEqual(agent["weight"], 1.4)
        self.assertEqual(agent["role"], "Institutional diligence workstream: acquisition")
        self.assertEqual(
            agent["focus_components"],
            ["cap_rate", "cash_on_cash", "rehab_load", "data_quality"],
        )
        self.assertIsInstance(agent["sources"], list)


if __name__ == "__main__":
    unittest.main()
