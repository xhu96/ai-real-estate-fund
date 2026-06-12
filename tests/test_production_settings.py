from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from ai_real_estate_fund.production.settings import ProductionSettings


class ProductionSettingsTest(unittest.TestCase):
    def test_production_requires_secret_and_api_key(self) -> None:
        with patch.dict(os.environ, {"APP_ENV": "production", "SECRET_KEY": "dev-secret-change-me", "REQUIRE_API_KEY": "false"}, clear=True):
            settings = ProductionSettings.from_env()
            issues = {issue.name: issue for issue in settings.validate()}
        self.assertIn("secret_key", issues)
        self.assertIn("api_keys", issues)
        self.assertIn("api_key_required", issues)

    def test_safe_staging_config_has_no_failures(self) -> None:
        env = {
            "APP_ENV": "staging",
            "SECRET_KEY": "x" * 40,
            "REQUIRE_API_KEY": "true",
            "API_KEYS": "operator:raw:admin",
            "ENABLE_DEMO_MODE": "false",
            "RATE_LIMIT_PER_MINUTE": "60",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = ProductionSettings.from_env()
        self.assertEqual(settings.environment, "staging")
        self.assertFalse([issue for issue in settings.validate() if issue.severity == "fail"])
        self.assertEqual(settings.api_keys, ("operator:raw:admin",))

    def test_redacted_hides_secrets(self) -> None:
        settings = ProductionSettings(secret_key="super-secret", api_keys=("name:key:admin",), api_key_hashes=("abc1234567890",))
        redacted = settings.redacted()
        self.assertEqual(redacted["secret_key"], "***")
        self.assertEqual(redacted["api_keys"], ("***",))
        self.assertTrue(str(redacted["api_key_hashes"][0]).endswith("..."))


if __name__ == "__main__":
    unittest.main()
