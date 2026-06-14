from __future__ import annotations

import dataclasses
import unittest

# Reuse the in-process ASGI client harness and example payload from phase 1.
from tests.test_phase1_api import _client, _example_payload


class Phase2ApiTest(unittest.TestCase):
    def setUp(self) -> None:
        # Force demo-open defaults for every test, regardless of ambient env.
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

    def _seed_run(self, client) -> str:
        created = client.post("/analyses", json=_example_payload())
        self.assertEqual(created.status_code, 200, created.text)
        return created.json()["run_id"]

    # (1) GET /analyses/{run_id} -----------------------------------------
    def test_get_analysis_by_run_id_returns_same_run(self) -> None:
        client = _client()
        run_id = self._seed_run(client)

        fetched = client.get(f"/analyses/{run_id}")
        self.assertEqual(fetched.status_code, 200, fetched.text)
        body = fetched.json()
        self.assertEqual(body["run_id"], run_id)
        # full decision dict shape
        for key in ("property", "metrics", "overall_score", "recommendation", "findings"):
            self.assertIn(key, body)

    def test_get_analysis_unknown_run_id_returns_404(self) -> None:
        client = _client()
        response = client.get("/analyses/does-not-exist-12345")
        self.assertEqual(response.status_code, 404, response.text)
        self.assertIn("detail", response.json())

    # (2) POST /portfolio/optimize-runs ----------------------------------
    def test_optimize_runs_returns_budget_candidates_plan(self) -> None:
        client = _client()
        self._seed_run(client)

        response = client.post("/portfolio/optimize-runs", json={"total_equity_budget": 1_000_000})
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(set(body.keys()), {"budget", "candidates", "plan"})
        self.assertEqual(body["budget"], 1_000_000)
        self.assertIsInstance(body["candidates"], list)
        self.assertGreaterEqual(len(body["candidates"]), 1)
        cand = body["candidates"][0]
        self.assertEqual(
            set(cand.keys()),
            {
                "name",
                "market",
                "score",
                "risk_score",
                "required_equity",
                "expected_irr",
                "cash_on_cash_return",
                "cap_rate",
                "recommendation",
            },
        )
        plan = body["plan"]
        self.assertEqual(set(plan.keys()), {"selected", "rejected", "equity_used", "reserves", "notes"})

    def test_optimize_runs_with_explicit_run_ids(self) -> None:
        client = _client()
        run_id = self._seed_run(client)

        response = client.post(
            "/portfolio/optimize-runs",
            json={"total_equity_budget": 2_000_000, "run_ids": [run_id]},
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(len(body["candidates"]), 1)

    def test_optimize_runs_missing_budget_returns_422(self) -> None:
        client = _client()
        response = client.post("/portfolio/optimize-runs", json={})
        self.assertEqual(response.status_code, 422, response.text)

    # (3) POST /research/backtest ----------------------------------------
    def test_backtest_defaults_returns_result(self) -> None:
        client = _client()
        response = client.post("/research/backtest", json={})
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        for key in (
            "trades",
            "selected_count",
            "hit_rate",
            "average_realized_irr",
            "average_model_score",
            "ending_equity",
        ):
            self.assertIn(key, body)
        self.assertIsInstance(body["trades"], list)
        if body["trades"]:
            trade = body["trades"][0]
            self.assertEqual(
                set(trade.keys()),
                {
                    "deal_name",
                    "selected",
                    "score",
                    "recommendation",
                    "expected_irr",
                    "realized_irr",
                    "realized_equity_multiple",
                },
            )

    def test_backtest_tuned_body_returns_200(self) -> None:
        client = _client()
        response = client.post("/research/backtest", json={"min_score": 90})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("ending_equity", response.json())


class RiskScoreMappingTest(unittest.TestCase):
    def test_risk_score_picks_named_risk_agent_not_role_text(self) -> None:
        # Regression: many agents mention "risk" in their role *description*; the
        # mapper must pick the agent whose NAME is the risk agent, not the first
        # finding whose role text happens to contain "risk".
        from app.backend.services.portfolio_service import _risk_score

        decision = {
            "overall_score": 70.0,
            "findings": [
                {"agent_name": "Debt Capital Markets Agent",
                 "role": "Evaluates interest-rate exposure and refinancing risk", "score": 57.6},
                {"agent_name": "Lease-Up Agent",
                 "role": "Estimates risk around vacancy and concessions", "score": 39.5},
                {"agent_name": "Risk Manager Agent",
                 "role": "Synthesizes downside risks and hard-pass triggers", "score": 56.2},
            ],
        }
        self.assertEqual(_risk_score(decision), 56.2)

    def test_risk_score_falls_back_to_overall_when_no_risk_agent(self) -> None:
        from app.backend.services.portfolio_service import _risk_score

        self.assertEqual(
            _risk_score({"overall_score": 64.0, "findings": [{"agent_name": "Market Agent", "score": 80.0}]}),
            64.0,
        )


if __name__ == "__main__":
    unittest.main()
