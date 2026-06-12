from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class BackendV6Test(unittest.TestCase):
    def test_create_app_and_health(self) -> None:
        try:
            from fastapi.testclient import TestClient
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"FastAPI TestClient unavailable: {exc}")
        with patch.dict(os.environ, {"APP_ENV": "development", "ENABLE_DEMO_MODE": "true", "REQUIRE_API_KEY": "false"}, clear=False):
            from app.backend.main import create_app
            app = create_app()
            client = TestClient(app)
            response = client.get("/ops/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_institutional_analyze_endpoint_demo_mode(self) -> None:
        try:
            from fastapi.testclient import TestClient
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"FastAPI TestClient unavailable: {exc}")
        from ai_real_estate_fund.data_loader import load_property
        with patch.dict(os.environ, {"APP_ENV": "development", "ENABLE_DEMO_MODE": "true", "REQUIRE_API_KEY": "false"}, clear=False):
            from app.backend.main import create_app
            app = create_app()
            client = TestClient(app)
            response = client.post("/institutional/analyze", json=load_property("examples/duplex_sunbelt.json").to_dict())
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("model_risk", payload)
        self.assertGreaterEqual(len(payload["findings"]), 10)


if __name__ == "__main__":
    unittest.main()
